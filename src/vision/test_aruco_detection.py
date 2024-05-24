import cv2
from chessviz import ChessViz

chessviz = ChessViz([[190, 390], 410], [[230, 420], 349], cam_index=1)
chessviz.test_aruco_detection(100)