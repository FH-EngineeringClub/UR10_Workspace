import cv2
import os
import sys

# Create the directory for storing images if it doesn't exist
if not os.path.exists('jpgs'):
    os.makedirs('jpgs')

# Start capturing video from the webcam (default device index is 0)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    sys.exit()

# Image counter
img_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    cv2.imshow("Camera", frame)

    key = cv2.waitKey(1)

    if key == ord(' '):  # Space bar pressed
        
        img_name = os.path.join("jpgs", f"img_{img_counter}.jpg")
        cv2.imwrite(img_name, frame)
        print(f"{img_name} saved.")
        img_counter += 1
    elif key == ord('q'):  # 'q' pressed
        print("Exiting...")
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()