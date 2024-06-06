import numpy as np
import cv2 as cv
import glob
import pickle
import os

vertices_x = 8
vertices_y = 6
# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((vertices_x*vertices_y,3), np.float32)
objp[:,:2] = np.mgrid[0:vertices_x,0:vertices_y].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob(os.path.join("jpgs", "*.jpg"))

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (vertices_x,vertices_y), None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)

    # Draw and display the corners
    cv.drawChessboardCorners(img, (vertices_x,vertices_y), corners2, ret)
    cv.imshow('img', img)
    cv.waitKey(500)

cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, 
                                                  gray.shape[::-1], None, None)

# Define the data to be saved
calibration_data = {
    "ret": ret,
    "mtx": mtx,
    "dist": dist,
    "rvecs": rvecs,
    "tvecs": tvecs
}

# Save the calibration data to a pickle file
with open('calibration_data.pkl', 'wb') as f:
    pickle.dump(calibration_data, f)

print("Calibration data saved to 'calibration_data.pkl'")