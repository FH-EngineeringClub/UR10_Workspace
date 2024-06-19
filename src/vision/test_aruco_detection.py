import cv2
from chessviz import ChessViz
import threading

PIECE_HEIGHTS = {
    "k": 0.08049 - 0.003,
    "K": 0.08049 - 0.001,
    "p": 0.03345 + 0.002,  # add 2mm to the height of the pawn
    "P": 0.03345 + 0.002,  # add 2mm to the height of the pawn
    "r": 0.053 - 0.008,
    "R": 0.053 - 0.008,
    "n": 0.04569,
    "N": 0.04569,
    "b": 0.05902 - 0.002,
    "B": 0.05902 - 0.002,
    "q": 0.068 + 0.002,
    "Q": 0.068 + 0.002,
}  # dictionary to store the heights of the pieces in meters

sample_size=20
chessviz = ChessViz([[190, 390], 410], [[230, 424], 348], PIECE_HEIGHTS, cam_index=0)
vision_thread = threading.Thread(target=chessviz.chess_array_update_thread, 
                       args=(sample_size,))
lock = threading.Lock()
vision_thread.start()

while True:
    print("Press enter to register move.")
    input()
    chessviz.counter_on.clear()
    chessviz.counter_on.wait()
    
    with lock:
        print(chessviz.chess_array)