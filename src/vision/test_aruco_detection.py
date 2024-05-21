import cv2
from chessviz import ChessViz

chessviz = ChessViz([0, 0], 300, 300, cam_index=0)
chessviz.test_aruco_detection()