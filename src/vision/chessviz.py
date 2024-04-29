import cv2
import numpy as np
from tkinter import *
from PIL import Image, ImageTk

OCCUPIED_THRESHOLD = 50
VARIANCE = 5
RESOLUTION_WIDTH = 1280
RESOLUTION_HEIGHT = 720
cam_index = 1
crop_width = 350
crop_height = 350
crop_origin = [180, 415]

def __update_crop_params(x_var, y_var, width_var, height_var):
    global crop_origin, crop_width, crop_height
    crop_origin[0] = int(x_var.get())
    crop_origin[1] = int(y_var.get())
    crop_width = int(width_var.get())
    crop_height = int(height_var.get())

def __show_frame(cap, lmain):
    _, frame = cap.read()
    cropped_frame = frame[crop_origin[1]:(crop_origin[1] + crop_height), 
                          crop_origin[0]:(crop_origin[0] + crop_width)]
    cv_img = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(cv_img)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, lambda: __show_frame(cap, lmain))

def __play_video_2():
    cap = cv2.VideoCapture(cam_index)

    root = Tk()
    root.bind('<Escape>', lambda e: root.quit())
    lmain = Label(root)
    lmain.pack()

    # Sliders for cropping parameters
    frame_x = Frame(root)
    frame_x.pack(fill='x', expand=True)
    x_var = StringVar()
    x_slider = Scale(frame_x, from_=0, to=RESOLUTION_WIDTH - 1, orient=HORIZONTAL, variable=x_var, label="X Origin")
    x_entry = Entry(frame_x, textvariable=x_var, width=5)
    x_slider.pack(side='left')
    x_entry.pack(side='left')

    frame_y = Frame(root)
    frame_y.pack(fill='x', expand=True)
    y_var = StringVar()
    y_slider = Scale(frame_y, from_=0, to=RESOLUTION_HEIGHT - 1, orient=HORIZONTAL, variable=y_var, label="Y Origin")
    y_entry = Entry(frame_y, textvariable=y_var)
    y_slider.pack(side='left')
    y_entry.pack(side='left')

    frame_width = Frame(root)
    frame_width.pack(fill='x', expand=True)
    width_var = StringVar()
    width_slider = Scale(frame_width, from_=1, to=RESOLUTION_WIDTH - 1, orient=HORIZONTAL, variable=width_var, label="Crop Width")
    width_entry = Entry(frame_width, textvariable=width_var)
    width_slider.pack(side='left')
    width_entry.pack(side='left')

    frame_height = Frame(root)
    frame_height.pack(fill='x', expand=True)
    height_var = StringVar()
    height_slider = Scale(root, from_=1, to=RESOLUTION_HEIGHT - 1, orient=HORIZONTAL, variable=height_var, label="Crop Height")
    height_entry = Entry(root, textvariable=height_var)
    height_slider.pack(side='left')
    height_entry.pack(side='left')
    
    # Button to update cropping parameters
    button = Button(root, text="Update Crop", 
                    command=lambda: __update_crop_params(
                        x_var, y_var, width_var, height_var))
    button.pack()
    root.bind('<Return>', lambda event: __update_crop_params(x_var, y_var, width_var, height_var))

    __show_frame(cap, lmain)  # Start showing the frame
    root.mainloop()  # Start the GUI

    cap.release()

# For checking cropped frame
def __play_video(): 
    cam = cv2.VideoCapture(cam_index)
    
    while(cam.isOpened()):
        result, image = cam.read()
        if result == True: 
            cropped_image = image[crop_origin[1]:(crop_origin[1] + crop_height), 
                          crop_origin[0]:(crop_origin[0] + crop_width)]
            cv2.imshow('Frame', cropped_image)
            # Press Q on keyboard to exit 
            if cv2.waitKey(25) & 0xFF == ord('q'): 
                break
        else:
            raise "Error taking video"
        
    cam.release()
    cv2.destroyAllWindows()
        
        
def get_image():
    cam = cv2.VideoCapture(cam_index)
    result, image = cam.read()
    cam.release()
    if not result: 
        raise "Error taking image"
    
    cropped_image = image[crop_origin[1]:(crop_origin[1] + crop_height), 
                          crop_origin[0]:(crop_origin[0] + crop_width)]
    
    return cropped_image

# TODO: Uses canny edge detection to set crop_width, crop_height,
# and crop_origin automatically
def find_chessboard():
    pass

def create_squares_array(image):
    # Crop out chessboard from rest of the image
    cropped_image = image[crop_origin[1]:(crop_origin[1] + crop_height), 
                          crop_origin[0]:(crop_origin[0] + crop_width)]

    square_width = round(crop_width / 8)
    square_height = round(crop_height / 8)
    squares_array = np.empty((8, 8), dtype=object)

    # Crop out squares from chessboard and create 8 by 8 array of squares
    for i in range(8):
        for j in range(8):
            squares_array[i][j] = cropped_image[i * square_width:(i + 1) * square_width,
                                                j * square_height:(j + 1) * square_height] # TODO: Might need to swap x and y
            
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
