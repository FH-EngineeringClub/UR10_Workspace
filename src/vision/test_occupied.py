from chessviz import ChessViz
import matplotlib.pyplot as plt
import cv2

viz = ChessViz([0, 0], 640, 480, cam_index=0)
image = viz.get_image()
image = viz.get_chessboard(image)
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imshow('image', image)
cv2.waitKey(0)

squares_array = viz.create_squares_array(image)
# print("shape before:", squares_array[0][0].shape)
# viz.skim_squares_array(squares_array)
# print("shape after:", squares_array[0][0].shape)

# display squares_array
fig, axes = plt.subplots(nrows=8, ncols=8, figsize=(8, 8))
# Flatten the axes array for easier indexing
axes = axes.flatten()

# Loop through each subplot and fill it with the corresponding sub-array data
for i in range(64):
    row, col = divmod(i, 8)
    ax = axes[i]
    # Display the sub-array at position (row, col) as a grayscale image
    ax.imshow(squares_array[row, col], cmap='gray', interpolation='nearest')
    ax.axis('off')  # Turn off axis numbering and ticks

# Adjust layout to prevent overlap
plt.tight_layout()
# Display the figure
# viz.find_threshold_values(squares_array)
plt.show()


