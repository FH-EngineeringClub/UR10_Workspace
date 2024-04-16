import chessviz as viz
import matplotlib.pyplot as plt
import cv2


image = viz.get_image()
cv2.imshow('og', image)
cv2.waitKey(0)
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
squares_array = viz.create_squares_array(image)

# display squares_array
fig, axes = plt.subplots(nrows=8, ncols=8, figsize=(12, 12))
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
plt.show()
viz.find_occupied_from_threshold(squares_array)