import numpy as np
import cv2
import pickle as pkl
from collections import deque

ARUCO_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
SIDELENGTH = 22.225
HEIGHT = 52
BUFFER_SIZE = 10

# Initialize a deque with a maximum length of 10
bufferx = deque(maxlen=BUFFER_SIZE)
buffery = deque(maxlen=BUFFER_SIZE)

def add_value(value):
    buffery.append(value[0])
    bufferx.append(value[1])

    averagey = int(sum(buffery) / len(buffery))
    averagex = int(sum(bufferx) / len(bufferx))
    return (averagey, averagex)

def get_centers(corners):
    list = []
    for marker_corners in corners: 
        # Extract the marker corners
        corners = marker_corners.reshape((4, 2))
        (top_left, top_right, bottom_right, bottom_left) = corners
        # Calculate and draw the center of the ArUco marker
        center_y = int((top_left[0] + bottom_right[0]) / 2.0)
        center_x = int((top_left[1] + bottom_right[1]) / 2.0)
        list.append([center_y, center_x])
    
    return list

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
with open('calibration_data.pkl', 'rb') as f:
    ret, mtx, dist, rvecs, tvecs = pkl.load(f)

aruco_detector = cv2.aruco.ArucoDetector(ARUCO_DICT)
while True: 
    result, image = cam.read()
    corners, ids, rejected = aruco_detector.detectMarkers(image)
    if len(corners) > 0:
        # get center point and draw it
        centers = get_centers(corners)
        
        # first start by getting tvec and rvec of marker from world to camera
        marker_coordinates = np.array([[-1 * SIDELENGTH / 2, SIDELENGTH / 2, 0], 
                            [SIDELENGTH / 2, SIDELENGTH / 2, 0], 
                            [SIDELENGTH / 2, -1 * SIDELENGTH / 2, 0],
                            [-1 * SIDELENGTH / 2, -1 * SIDELENGTH / 2, 0]], dtype=np.float32)
        height_vector = np.array([0, 0, -1 * HEIGHT])

        for center, marker_corners in zip(centers, corners):
            marker_corners = marker_corners.reshape(4, 2)
            retval, rvec, tvec = cv2.solvePnP(marker_coordinates, marker_corners, mtx, dist, useExtrinsicGuess=False, flags=cv2.SOLVEPNP_IPPE_SQUARE)

            # pose = cv2.drawFrameAxes(image, mtx, dist, rvec, tvec, HEIGHT, 2)
            # transform rvec into matrix using rodrigues method
            rotation_matrix = np.zeros((3, 3))
            cv2.Rodrigues(rvec, rotation_matrix)

            # Ensure the Z-axis direction is always negative
            if rotation_matrix[2, 2] > 0:
                rotation_matrix[:, 2] = -rotation_matrix[:, 2]

            transformed_height_vector = rotation_matrix.dot(height_vector)
            endpoint_3D = tvec + transformed_height_vector.reshape(-1, 1)

            endpoint_2D = mtx.dot(endpoint_3D)
            endpoint_2D = (int(endpoint_2D[0] / endpoint_2D[2]), int(endpoint_2D[1] / endpoint_2D[2]))
            average = add_value(endpoint_2D)
            cv2.line(image, center, average, (0, 255, 0), 2)
    cv2.imshow('Pose', image)
    key = cv2.waitKey(1)

    if key == ord('q'):
        print("Exiting")
        break

print(image.shape)

cam.release()