import cv2
from chessviz import ChessViz
import threading

sample_size=20
chessviz = ChessViz([[190, 390], 410], [[230, 424], 348], cam_index=1)
vision_thread = threading.Thread(target=chessviz.chess_array_update_thread, 
                       args=(sample_size,))
lock = threading.Lock()
vision_thread.start()

try:
    while True:
        print("Press enter to register move.")
        input()
        chessviz.counter_on.clear()
        chessviz.counter_on.wait()
        
        with lock:
            print(chessviz.chess_array)

except KeyboardInterrupt:
    print("Exiting program")
    chessviz.shutdown.set()
    vision_thread.join()