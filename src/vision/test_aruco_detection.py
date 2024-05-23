import cv2
from chessviz import ChessViz

chessviz = ChessViz([[0, 0], 400], [[25, 25], 300], cam_index=0)
chessviz.test_aruco_detection()