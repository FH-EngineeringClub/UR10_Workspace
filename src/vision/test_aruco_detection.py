import cv2
from chessviz import ChessViz

chessviz = ChessViz([[240, 450], 300], [[255, 474], 264], cam_index=1)
chessviz.test_aruco_detection(100)