# Neuropil Utils - シンプルな使用例（ノートブック用）

# ライブラリをインポート
from neuropil_utils import create_neuropil_viewer

# 画像とラベルのパスを設定
image_path = "/Users/sakanotakumi/Documents/000_Home/Work/Research/02_Experiments_data/E343/data/imagesTs-1.tif"
labels_path = "/Users/sakanotakumi/Documents/000_Home/Work/Research/02_Experiments_data/E343/data/vol2_ensemble-1_ws.tif"

# 完全なneuropil分析用のnapariビューアーを作成
viewer, transfer_widget, save_widget = create_neuropil_viewer(image_path, labels_path)

# napariを実行（この行はノートブックでは通常コメントアウト）
# napari.run()

print("Neuropil viewer created successfully!")
print("Available functions:")
print("- Transfer widget: labels間でのcut & paste")
print("- Save widget: labelsをPNGファイルとして保存")
