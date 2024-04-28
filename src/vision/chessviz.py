import cv2
import numpy as np

OCCUPIED_THRESHOLD = 50
VARIANCE = 5
cam_index = 0
crop_width = 400
crop_height = 400
crop_origin = [5, 5]

def get_image():
    cam = cv2.VideoCapture(cam_index)
    result, image = cam.read()
    cam.release()
    if not result: 
        raise "Error taking image"
    
    return image

# TODO: Uses canny edge detection to set crop_width, crop_height,
# and crop_origin automatically
def find_chessboard():
    pass

def create_squares_array(image):
    # Crop out chessboard from rest of the image
    cropped_image = image[crop_origin[0]:(crop_origin[0] + crop_width), 
                         crop_origin[1]:(crop_origin[1] + crop_height)]

    square_width = round(crop_width / 8)
    square_height = round(crop_height / 8)
    squares_array = np.empty((8, 8), dtype=object)

    # Crop out squares from chessboard and create 8 by 8 array of squares
    for i in range(8):
        for j in range(8):
            squares_array[i][j] = cropped_image[i * square_width:(i + 1) * square_width,
                                                j * square_height:(j + 1) * square_height]
            
    return squares_array

# Exists for sole purpose of numpy vectorization
def __calculate_mean(array):
    return round(np.mean(array))

def find_occupied_from_threshold(squares_array):
    # Vectorize function in order to make it numpy iterable
    vectorized_mean = np.vectorize(__calculate_mean)
    average_values = vectorized_mean(squares_array)
    mask = ((average_values > OCCUPIED_THRESHOLD - VARIANCE) & 
                      (average_values < OCCUPIED_THRESHOLD + VARIANCE))

    occupied_array = np.zeros((8, 8))
    occupied_array[mask] = 1
    return occupied_array
