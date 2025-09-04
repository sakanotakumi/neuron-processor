# neuron-processor
napari-based tools for refining neuron annotations \
napariを使用したneuropil分析のためのユーティリティライブラリです。

## 機能

- **画像読み込み**: z-stackされたTIFF画像の読み込み
- **napariビューアー**: 画像とラベルの表示
- **ラベル転送ウィジェット**: レイヤー間でのラベルのcut & paste
- **ラベル保存ウィジェット**: ラベルをPNGファイルとして保存

## ファイル構成

- `neuropil_utils.py` - メインライブラリ
- `example_usage.py` - 詳細な使用例
- `simple_usage.py` - シンプルな使用例（ノートブック用）

## 使用方法

### 基本的な使用方法

```python
from neuropil_utils import create_neuropil_viewer

# 画像とラベルのパスを設定
image_path = "path/to/images.tif"
labels_path = "path/to/labels.tif"

# 完全なneuropil分析用のnapariビューアーを作成
viewer, transfer_widget, save_widget = create_neuropil_viewer(image_path, labels_path)

# napariを実行
napari.run()
```

### ノートブックでの使用方法

```python
# ノートブックのセルで実行
from neuropil_utils import create_neuropil_viewer

image_path = "path/to/images.tif"
labels_path = "path/to/labels.tif"

viewer, transfer_widget, save_widget = create_neuropil_viewer(image_path, labels_path)
# napari.run()は通常コメントアウト
```

### 個別の機能を使用する場合

```python
from neuropil_utils import setup_napari_viewer, setup_widgets

# ビューアーのみを作成
viewer = setup_napari_viewer(image_path, labels_path)

# ウィジェットを後から追加
transfer_widget, save_widget = setup_widgets(viewer)
```

## 主要クラス

### LabelTransferWidget
- レイヤー間でのラベル転送機能
- ポイントレイヤーで指定した位置のラベルをcut & paste

### LabelSaveWidget
- ラベルデータをPNGファイルとして保存
- z-stackの各スライスを個別のPNGファイルとして出力

## 依存関係

- napari
- numpy
- scikit-image
- pathlib
- qtpy
- scipy

## インストール

このライブラリを使用するには、必要な依存関係がインストールされている必要があります：

```bash
pip install -r requirements.txt
```
