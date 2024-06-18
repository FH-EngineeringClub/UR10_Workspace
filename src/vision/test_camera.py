import numpy as np
import cv2
import pickle as pkl

ARUCO_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

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
    result, image = cam.read()
    h, w = image.shape[:2]
    ret, mtx, dist, rvecs, tvecs = pkl.load(f)
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, 
        (w, h)
        )

aruco_detector = cv2.aruco.ArucoDetector(ARUCO_DICT)
while True: 
    result, image = cam.read()
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # image = cv2.undistort(image, mtx, dist, newCameraMatrix=newcameramtx)
    corners, ids, rejected = aruco_detector.detectMarkers(image)
    if len(corners) > 0:
        # get center point and draw it
        centers = get_centers(corners)
        # for center in centers:
        #     cv2.circle(image, center, 4, (0, 0, 255), -1)
        
        # first start by getting tvec and rvec of marker from world to camera
        SIDELENGTH = 20
        HEIGHT = 52
        marker_coordinates = np.array([[-1 * SIDELENGTH / 2, SIDELENGTH / 2, 0], 
                            [SIDELENGTH / 2, SIDELENGTH / 2, 0], 
                            [SIDELENGTH / 2, -1 * SIDELENGTH / 2, 0],
                            [-1 * SIDELENGTH / 2, -1 * SIDELENGTH / 2, 0]], dtype=np.float32)
        height_vector = np.array([0, 0, -1 * HEIGHT])

        for center, marker_corners in zip(centers, corners):
            marker_corners = marker_corners.reshape(4, 2)
            retval, rvec, tvec = cv2.solvePnP(marker_coordinates, marker_corners, mtx, dist, useExtrinsicGuess=False, flags=cv2.SOLVEPNP_IPPE_SQUARE)

            pose = cv2.drawFrameAxes(image, mtx, dist, rvec, tvec, HEIGHT, 2)
            # # transform rvec into matrix using rodrigues method
            # rotation_matrix = np.zeros((3, 3))
            # cv2.Rodrigues(rvec, rotation_matrix)

            # transformed_height_vector = rotation_matrix.dot(height_vector)
            # endpoint_3D = tvec + transformed_height_vector.reshape(-1, 1)

            # endpoint_2D = mtx.dot(endpoint_3D)
            # endpoint_2D = (int(endpoint_2D[0] / endpoint_2D[2]), int(endpoint_2D[1] / endpoint_2D[2]))
            # cv2.line(image, center, endpoint_2D, (0, 255, 0), 2)
        cv2.imshow('Pose', image)
        key = cv2.waitKey(1)

        if key == ord('q'):
            print("Exiting")
            break

print(image.shape)

cam.release()