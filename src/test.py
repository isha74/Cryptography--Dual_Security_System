import pydicom
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Load DICOM file
ds = pydicom.dcmread("Data/0002.DCM")
frames = ds.pixel_array

# Create side-by-side subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

# Left: Single frame
ax1.imshow(frames[0], cmap=plt.cm.gray)
ax1.set_title("First Frame")
ax1.axis('off')

# Right: Animation
im = ax2.imshow(frames[0], cmap=plt.cm.gray)
ax2.set_title("Animation")
ax2.axis('off')

# Animation update function
def update(frame_index):
    im.set_array(frames[frame_index])
    return [im]

# Create animation
ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=50)

plt.tight_layout()
plt.show()
