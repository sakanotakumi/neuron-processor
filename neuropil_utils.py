"""
Neuropil analysis utilities for napari-based image processing
"""

import napari
import numpy as np
from pathlib import Path
from skimage import io
import os
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QFileDialog
from qtpy.QtCore import Qt
from scipy import ndimage
from typing import Optional, Tuple, List, Union


def load_zstack_tiff(file_path):
    """
    z-stackされたTIFF画像を読み込む関数
    
    Args:
        file_path (str): TIFFファイルのパス
        
    Returns:
        numpy.ndarray: z-stack画像データ
    """
    try:
        image = io.imread(file_path)
        print(f"Loaded z-stack TIFF: {Path(file_path).name}, shape: {image.shape}")
        return image
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def load_images_from_directory(directory_path, supported_formats=('.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp')):
    """
    指定されたディレクトリから画像を読み込む関数
    
    Args:
        directory_path (str): ディレクトリのパス
        supported_formats (tuple): サポートされる画像形式
        
    Returns:
        tuple: (images, names) - 読み込まれた画像のリストと名前のリスト
    """
    directory = Path(directory_path)
    images = []
    names = []
    
    if directory.exists():
        for image_file in sorted(directory.iterdir()):
            if image_file.suffix.lower() in supported_formats:
                image = io.imread(image_file)
                images.append(image)
                names.append(image_file.stem)
                print(f"Loaded: {image_file.name}")
    else:
        print(f"Directory {directory_path} does not exist")
    
    return images, names


def setup_napari_viewer(images_path, labels_path):
    """
    napariビューアーをセットアップし、画像とラベルを読み込む
    
    Args:
        images_path (str): 画像ファイルのパス
        labels_path (str): ラベルファイルのパス
        
    Returns:
        napari.Viewer: 設定済みのnapariビューアー
    """
    # 画像ファイルを読み込み
    images = load_zstack_tiff(images_path)
    labels = load_zstack_tiff(labels_path)

    if images is None or labels is None:
        raise ValueError("Failed to load images or labels")

    # napariビューアーを作成
    viewer = napari.Viewer()

    # napariにz-stack画像として追加
    viewer.add_image(images, name="Images")
    viewer.add_labels(labels, name="Labels")
    
    return viewer


class LabelTransferWidget(QWidget):
    """ラベル転送用のウィジェット"""
    
    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)  # スペーシングを小さく
        
        # From layer selection
        from_layout = QHBoxLayout()
        from_layout.addWidget(QLabel("From:"))
        self.from_combo = QComboBox()
        self.from_combo.setMinimumWidth(100)  # 最小幅を設定
        from_layout.addWidget(self.from_combo)
        layout.addLayout(from_layout)
        
        # To layer selection
        to_layout = QHBoxLayout()
        to_layout.addWidget(QLabel("To:"))
        self.to_combo = QComboBox()
        self.to_combo.setMinimumWidth(100)
        to_layout.addWidget(self.to_combo)
        layout.addLayout(to_layout)
        
        # Point layer selection
        point_layout = QHBoxLayout()
        point_layout.addWidget(QLabel("Points:"))
        self.point_combo = QComboBox()
        self.point_combo.setMinimumWidth(100)
        point_layout.addWidget(self.point_combo)
        layout.addLayout(point_layout)
        
        # Buttons
        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update_layer_lists)
        layout.addWidget(self.update_button)
        
        self.transfer_button = QPushButton("Cut & Paste")
        self.transfer_button.clicked.connect(self.transfer_labels)
        layout.addWidget(self.transfer_button)
        
        # ウィジェット全体のサイズを制限
        self.setMaximumWidth(200)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.setLayout(layout)
        self.update_layer_lists()
        
        # Connect to layer events
        self.viewer.layers.events.inserted.connect(self.update_layer_lists)
        self.viewer.layers.events.removed.connect(self.update_layer_lists)
    
    def update_layer_lists(self):
        self.from_combo.clear()
        self.to_combo.clear()
        self.point_combo.clear()
        
        for layer in self.viewer.layers:
            if hasattr(layer, 'data') and 'Labels' in str(type(layer)):
                self.from_combo.addItem(layer.name)
                self.to_combo.addItem(layer.name)
            elif hasattr(layer, 'data') and 'Points' in str(type(layer)):
                self.point_combo.addItem(layer.name)
    
    def transfer_labels(self):
        from_layer_name = self.from_combo.currentText()
        to_layer_name = self.to_combo.currentText()
        point_layer_name = self.point_combo.currentText()
        
        if not all([from_layer_name, to_layer_name, point_layer_name]):
            print("Please select all required layers")
            return
        
        from_layer = None
        to_layer = None
        point_layer = None
        
        for layer in self.viewer.layers:
            if layer.name == from_layer_name:
                from_layer = layer
            elif layer.name == to_layer_name:
                to_layer = layer
            elif layer.name == point_layer_name:
                point_layer = layer
        
        if not all([from_layer, to_layer, point_layer]):
            print("Could not find selected layers")
            return
        
        points = point_layer.data
        if len(points) == 0:
            print("No points found in point layer")
            return
        
        for point in points:
            point_indices = tuple(int(coord) for coord in point)
            
            if any(idx < 0 or idx >= dim for idx, dim in zip(point_indices, from_layer.data.shape)):
                continue
            
            label_value = from_layer.data[point_indices]
            
            if label_value == 0:
                continue
            
            label_mask = (from_layer.data == label_value)
            to_layer.data[label_mask] = label_value
            from_layer.data[label_mask] = 0
        
        point_layer.data = []
        from_layer.refresh()
        to_layer.refresh()
        point_layer.refresh()
        print(f"Labels transferred from '{from_layer_name}' to '{to_layer_name}' and points cleared")


class LabelSaveWidget(QWidget):
    """ラベル保存用のウィジェット"""
    
    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self.save_directory = Path("saved_labels_png")
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Layer selection
        layer_layout = QHBoxLayout()
        layer_layout.addWidget(QLabel("Layer:"))
        self.save_combo = QComboBox()
        self.save_combo.setMinimumWidth(100)
        layer_layout.addWidget(self.save_combo)
        layout.addLayout(layer_layout)
        
        # Directory selection - 短縮表示
        dir_layout = QVBoxLayout()
        dir_layout.addWidget(QLabel("Save Directory:"))
        self.dir_label = QLabel("saved_labels_png")
        self.dir_label.setStyleSheet("border: 1px solid gray; padding: 2px; font-size: 10px;")
        self.dir_label.setWordWrap(True)  # テキストの折り返しを有効に
        self.dir_label.setMaximumHeight(40)  # 高さを制限
        dir_layout.addWidget(self.dir_label)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.browse_button)
        layout.addLayout(dir_layout)
        
        # Buttons
        self.update_save_button = QPushButton("Update")
        self.update_save_button.clicked.connect(self.update_layer_list)
        layout.addWidget(self.update_save_button)
        
        self.save_button = QPushButton("Save PNG")
        self.save_button.clicked.connect(self.save_labels_as_png)
        layout.addWidget(self.save_button)
        
        # ウィジェット全体のサイズを制限
        self.setMaximumWidth(200)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.setLayout(layout)
        self.update_layer_list()
        
        self.viewer.layers.events.inserted.connect(self.update_layer_list)
        self.viewer.layers.events.removed.connect(self.update_layer_list)
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Directory to Save Labels",
            str(self.save_directory.parent)
        )
        if directory:
            self.save_directory = Path(directory)
            # パスを短縮して表示
            display_path = str(self.save_directory)
            if len(display_path) > 30:
                display_path = "..." + display_path[-27:]
            self.dir_label.setText(display_path)
    
    def update_layer_list(self):
        self.save_combo.clear()
        for layer in self.viewer.layers:
            if hasattr(layer, 'data') and 'Labels' in str(type(layer)):
                self.save_combo.addItem(layer.name)
    
    def save_labels_as_png(self):
        layer_name = self.save_combo.currentText()
        if not layer_name:
            print("Please select a layer to save")
            return
        
        selected_layer = None
        for layer in self.viewer.layers:
            if layer.name == layer_name:
                selected_layer = layer
                break
        
        if selected_layer is None:
            print("Could not find selected layer")
            return
        
        self.save_directory.mkdir(exist_ok=True)
        label_data = selected_layer.data
        
        for z_idx in range(label_data.shape[0]):
            slice_data = label_data[z_idx]
            slice_data = slice_data.astype(np.uint16)
            filename = self.save_directory / f"{z_idx:04d}.png"
            io.imsave(filename, slice_data)
        
        print(f"Saved {label_data.shape[0]} PNG files to {self.save_directory}")


def setup_widgets(viewer):
    """
    napariビューアーにウィジェットを追加する
    
    Args:
        viewer (napari.Viewer): napariビューアー
        
    Returns:
        tuple: (transfer_widget, save_widget) - 作成されたウィジェット
    """
    # ウィジェットを作成して追加
    transfer_widget = LabelTransferWidget(viewer)
    viewer.window.add_dock_widget(transfer_widget, name="Transfer", area="left")

    save_widget = LabelSaveWidget(viewer)
    viewer.window.add_dock_widget(save_widget, name="Save", area="left")
    
    return transfer_widget, save_widget


def create_neuropil_viewer(images_path, labels_path):
    """
    完全なneuropil分析用のnapariビューアーを作成する
    
    Args:
        images_path (str): 画像ファイルのパス
        labels_path (str): ラベルファイルのパス
        
    Returns:
        tuple: (viewer, transfer_widget, save_widget) - ビューアーとウィジェット
    """
    viewer = setup_napari_viewer(images_path, labels_path)
    transfer_widget, save_widget = setup_widgets(viewer)
    
    return viewer, transfer_widget, save_widget
