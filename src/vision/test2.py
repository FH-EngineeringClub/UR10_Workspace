import cv2

cam = cv2.VideoCapture(0)
result, image = cam.read()

print(image.shape)

cam.release()

