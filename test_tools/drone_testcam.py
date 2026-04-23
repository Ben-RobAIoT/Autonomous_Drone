import cv2
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if cap.isOpened():
    print("Camera mở thành công!")
else:
    print("Không thể mở Camera.")
cap.release()