"""
Neuropil Utils使用例

このスクリプトは、neuropil_utils.pyライブラリの使用方法を示します。
"""

import sys
from pathlib import Path

# ライブラリをインポート
from neuropil_utils import create_neuropil_viewer, setup_napari_viewer, setup_widgets
import napari

def main():
    """メイン関数"""
    
    # 画像とラベルのパスを設定
    image_path = "/Users/sakanotakumi/Documents/000_Home/Work/Research/02_Experiments_data/E343/data/imagesTs-1.tif"
    labels_path = "/Users/sakanotakumi/Documents/000_Home/Work/Research/02_Experiments_data/E343/data/vol2_ensemble-1_ws.tif"
    
    # 方法1: 完全なビューアーを一度に作成
    print("Creating complete neuropil viewer...")
    viewer, transfer_widget, save_widget = create_neuropil_viewer(image_path, labels_path)
    
    # 方法2: 段階的に作成（より細かい制御が必要な場合）
    # viewer = setup_napari_viewer(image_path, labels_path)
    # transfer_widget, save_widget = setup_widgets(viewer)
    
    # napariを実行
    napari.run()

if __name__ == "__main__":
    main()
