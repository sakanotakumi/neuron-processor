from neuropil_utils import load_zstack_tiff, load_images_from_directory
import numpy as np

dendrite_dir = "/Users/sakanotakumi/Documents/000_Home/Work/Research/02_Experiments_data/E343/output/dendrite"
axon_dir = "/Users/sakanotakumi/Documents/000_Home/Work/Research/02_Experiments_data/E343/output/axon"



dendrite = load_images_from_directory(dendrite_dir)
axon = load_images_from_directory(axon_dir)

dendrite_images = np.array(dendrite[0])
axon_images = np.array(axon[0])


from skimage import measure

# Get unique labels for dendrite (excluding 0)
dendrite_unique = np.unique(dendrite_images)
dendrite_unique = dendrite_unique[dendrite_unique > 0]  # Remove background (0)

# Create relabeling mapping for dendrite
dendrite_relabeled = np.zeros_like(dendrite_images)
for new_label, old_label in enumerate(dendrite_unique, start=1):
    dendrite_relabeled[dendrite_images == old_label] = new_label

# Get unique labels for axon (excluding 0)
axon_unique = np.unique(axon_images)
axon_unique = axon_unique[axon_unique > 0]  # Remove background (0)

# Create relabeling mapping for axon
axon_relabeled = np.zeros_like(axon_images)
for new_label, old_label in enumerate(axon_unique, start=1):
    axon_relabeled[axon_images == old_label] = new_label

print(f"Dendrite images re-labeled: {dendrite_relabeled.shape}")
print(f"Dendrite unique labels: {len(dendrite_unique)} (1 to {len(dendrite_unique)})")
print(f"Axon images re-labeled: {axon_relabeled.shape}")
print(f"Axon unique labels: {len(axon_unique)} (1 to {len(axon_unique)})")

import napari

# Create a napari viewer
viewer = napari.Viewer()

# Add dendrite relabeled as labels
viewer.add_labels(dendrite_relabeled, name='Dendrite Labels')

# Add axon relabeled as labels
viewer.add_labels(axon_relabeled, name='Axon Labels')

# Show the viewer
napari.run()