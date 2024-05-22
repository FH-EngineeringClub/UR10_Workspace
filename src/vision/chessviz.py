import cv2
import numpy as np
from tkinter import *
from PIL import Image, ImageTk

class ChessViz:
    def __init__(self, big_crop, small_crop, skim_percent=0.1, 
                 variance=5, occupied_threshold = 50, cam_index=1):
        self.big_crop = big_crop                        # [[y value, x value], width, height]
        self.small_crop = small_crop                    # [[y value, x value], width, height]
        self.skim_percent = skim_percent
        self.variance = variance
        self.occupied_threshold = occupied_threshold
        self.cam_index = cam_index

        # takes picture and determines resolution width and height
        # from picture dimensions
        cam = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        ret, image = cam.read() 
        self.resolution_width = image.shape[1]
        self.resolution_height = image.shape[0] 

    # For tkinter gui
    def __update_crop_params(self, crop_params, x_var, y_var, width_var, height_var):
        crop_params[0][1] = int(x_var.get())
        crop_params[0][0] = int(y_var.get())
        crop_params[1] = int(width_var.get())
        crop_params[2] = int(height_var.get())

    # For tkinter gui
    def __show_frame(self, crop_params, cap, lmain):
        _, frame = cap.read()
        cropped_frame = frame[crop_params[0][0]:(crop_params[0][0] + crop_params[2]), 
                            crop_params[0][1]:(crop_params[0][1] + crop_params[1])]
        cv_img = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv_img)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        lmain.after(10, lambda: self.__show_frame(crop_params, cap, lmain))

    # Uses tkinter gui to help dev find crop parameters, i.e. crop origin, 
    # crop width, and crop height
    def crop_gui(self, crop_id):
        if crop_id == 0: 
            crop_params = self.big_crop
        elif crop_id == 1:
            crop_params = self.small_crop
            
        cap = cv2.VideoCapture(self.cam_index, cv2.CAP_DSHOW)

        root = Tk()
        root.bind('<Escape>', lambda e: root.quit())
        lmain = Label(root)
        lmain.pack()

        # Sliders for cropping parameters
        frame_x = Frame(root)
        frame_x.pack(fill='x', expand=True)
        x_var = StringVar()
        x_slider = Scale(frame_x, from_=0, to=self.resolution_width - 1, 
                         orient=HORIZONTAL, variable=x_var, label="X Origin")
        x_entry = Entry(frame_x, textvariable=x_var, width=5)
        x_slider.pack(side='left')
        x_entry.pack(side='left')

        frame_y = Frame(root)
        frame_y.pack(fill='x', expand=True)
        y_var = StringVar()
        y_slider = Scale(frame_y, from_=0, to=self.resolution_height - 1, 
                         orient=HORIZONTAL, variable=y_var, label="Y Origin")
        y_entry = Entry(frame_y, textvariable=y_var)
        y_slider.pack(side='left')
        y_entry.pack(side='left')

        frame_width = Frame(root)
        frame_width.pack(fill='x', expand=True)
        width_var = StringVar()
        width_slider = Scale(frame_width, from_=1, to=self.resolution_width - 1, 
                             orient=HORIZONTAL, variable=width_var, 
                             label="Crop Width")
        width_entry = Entry(frame_width, textvariable=width_var)
        width_slider.pack(side='left')
        width_entry.pack(side='left')

        frame_height = Frame(root)
        frame_height.pack(fill='x', expand=True)
        height_var = StringVar()
        height_slider = Scale(root, from_=1, to=self.resolution_height - 1, 
                              orient=HORIZONTAL, variable=height_var, label="Crop Height")
        height_entry = Entry(root, textvariable=height_var)
        height_slider.pack(side='left')
        height_entry.pack(side='left')
        
        # Button to update cropping parameters
        button = Button(root, text="Update Crop", 
                        command=lambda: self.__update_crop_params(
                            crop_params, x_var, y_var, width_var, height_var))
        button.pack()
        root.bind('<Return>', lambda event: self.__update_crop_params(
            crop_params, x_var, y_var, width_var, height_var))

        self.__show_frame(crop_params, cap, lmain)  # Start showing the frame
        root.mainloop()  # Start the GUI

        cap.release()
            
    def get_image(self):
        cam = cv2.VideoCapture(self.cam_index, cv2.CAP_DSHOW)
        result, image = cam.read()
        cam.release()
        if not result: 
            raise "Error taking image"
        
        return image
    
    def get_crop(self, image, crop_params):
        return image[crop_params[0][0]:(crop_params[0][0] + crop_params[2]), 
                        crop_params[0][1]:(crop_params[0][1] + crop_params[1])]

    # TODO: Uses canny edge detection to set crop_width, crop_height,
    # and crop_origin automatically
    def find_chessboard():
        pass

    # Takes cropped chessboard and evenly splits crop into 8 by 8 squares
    # input: numpy array of shape (crop height, crop width)
    # output: numpy array of shape (8, 8, square height, square width)
    def create_squares_array(self, image):
        self.square_width = round(image.shape[1] / 8)
        self.square_height = round(image.shape[0] / 8)
        squares_array = np.empty((8, 8), dtype=object)

        # Crop out squares from chessboard and create 8 by 8 array of squares
        for i in range(8):
            for j in range(8):
                squares_array[i][j] = image[i * self.square_height:(i + 1) * self.square_height,
                                            j * self.square_width:(j + 1) * self.square_width,] 
                
        return squares_array

    # Since crop is not perfect, this function shaves off some percent of 
    # pixels off each squares' borders. The percent is defined in the global 
    # variable "skim_percent"
    # input: numpy array of shape (8, 8, square height, square width)
    # output: numpy array of shape (8, 8, square height - square height * skim percent,
    # square width - square width * skim percent)
    def skim_squares_array(self, squares_array):
        print("square_width: ", self.square_width)
        print("square_hegiht: ", self.square_height)
        for i in range(8):
            for j in range(8): 
                squares_array[i][j] = squares_array[i][j][round(self.skim_percent*self.square_height):
                                                          round(-self.skim_percent*self.square_height), 
                                                          round(self.skim_percent*self.square_width):
                                                          round(-self.skim_percent*self.square_width)]

    # Exists for sole purpose of numpy vectorization. Uses standard deviation of 
    # greyscale values in order to measure contrast within an image. A higher deviation
    # represents higher contrast and thus an increased likehood of a piece being in that 
    # square. 
    def __calculate_contrast(self, image):
        return np.round(image.std())

    # Takes squares array, finds standard deviation for each square, and applies a threshold
    # and variance(error) value to determine whether a square is filled or not. A value
    # of 1 indicates it is filled. A value of 0 indicates it is not.  
    # input: numpy array of shape (8, 8, square height - square height * skim percent,
    # square width - square width * skim percent)
    # output: numpy array of shape (8, 8, 1)
    def find_occupied_from_threshold(self, squares_array):
        # Vectorize function in order to make it numpy iterable
        vectorized_contrast = np.vectorize(self.__calculate_contrast)
        contrast_values = vectorized_contrast(squares_array)

        # if a contrast value is in a certain threshold +- some error, 
        # then the space is occupied
        mask = ((contrast_values > self.occupied_threshold - self.variance) & 
                        (contrast_values < self.occupied_threshold + self.variance))

        occupied_array = np.zeros((8, 8))
        occupied_array[mask] = 1
        return occupied_array

    # Simply prints a numpy array containing the standard deviation value for each 
    # sqaure. 
    # input: numpy array of shape (8, 8, square height - square height * skim percent,
    # square width - square width * skim percent)
    # output: numpy array of shape (8, 8, 1)
    def find_threshold_values(self, squares_array):
        # Vectorize function in order to make it numpy iterable
        vectorized_func = np.vectorize(self.__calculate_contrast)
        contrast_values = vectorized_func(squares_array)
        print(contrast_values)
        
    def get_centers(self, corners_array):
        center_array = np.empty((np.size(corners_array, 0), 2))
        
        for i in range(np.size(corners_array, 0)):
            corners = corners_array[i].reshape((4, 2))
            (top_left, top_right, bottom_right, bottom_left) = corners
            
            # Convert the (x,y) coordinate pairs to integers
            top_right = (int(top_right[0]), int(top_right[1]))
            bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
            bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
            top_left = (int(top_left[0]), int(top_left[1]))
        
            # Calculate and draw the center of the ArUco marker
            center_y = int((top_left[0] + bottom_right[0]) / 2.0)
            center_x = int((top_left[1] + bottom_right[1]) / 2.0)
            center_array[i] = (center_y, center_x)
            
        return center_array
    
    def get_chess_array(self, centers, ids, chess_image):
        pass
    
    def resize_image(self, image, factor):
        # Get the original image dimensions
        h, w = image.shape[:2]
        return cv2.resize(image, (round(factor * w), round(factor * h)))

    def test_aruco_detection(self):
        cap = cv2.VideoCapture(self.cam_index, cv2.CAP_DSHOW)
        total = 0
        detected = 0
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

        while(cap.isOpened()):
            ret, frame = cap.read()
            frame = self.get_chessboard(frame) 
            frame = self.resize_image(frame, 1)
            total += 1
            # Detect ArUco markers in the video frame
            (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, aruco_dict)
            # Check that at least one ArUco marker was detected
            if len(corners) > 0:
                if len(corners) == 32:
                    detected += 1
                
                # Flatten the ArUco IDs list
                # ids = ids.flatten()
                # # Loop over the detected ArUco corners
                for (marker_corner, marker_id) in zip(corners, ids):
            
                    # Extract the marker corners
                    corners = marker_corner.reshape((4, 2))
                    (top_left, top_right, bottom_right, bottom_left) = corners
                    
                    # Convert the (x,y) coordinate pairs to integers
                    top_right = (int(top_right[0]), int(top_right[1]))
                    bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
                    bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
                    top_left = (int(top_left[0]), int(top_left[1]))
                    
                    # Draw the bounding box of the ArUco detection
                    cv2.line(frame, top_left, top_right, (0, 255, 0), 2)
                    cv2.line(frame, top_right, bottom_right, (0, 255, 0), 2)
                    cv2.line(frame, bottom_right, bottom_left, (0, 255, 0), 2)
                    cv2.line(frame, bottom_left, top_left, (0, 255, 0), 2)
                    
                    # Calculate and draw the center of the ArUco marker
                    center_x = int((top_left[0] + bottom_right[0]) / 2.0)
                    center_y = int((top_left[1] + bottom_right[1]) / 2.0)
                    cv2.circle(frame, (center_x, center_y), 4, (0, 0, 255), -1)
                    
                    # Draw the ArUco marker ID on the video frame
                    # The ID is always located at the top_left of the ArUco marker
                    cv2.putText(frame, str(marker_id), 
                    (top_left[0], top_left[1] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
        
                # Display the resulting frame
            cv2.imshow('frame',frame)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        cv2.destroyAllWindows()
        cap.release()
            
        print("percent detected: ", 100 * detected / total, "%")