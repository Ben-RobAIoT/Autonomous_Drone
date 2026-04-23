# test_read.py
import cv2
import time

print("Đang khởi động Camera...")
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# Cấu hình độ phân giải cho IMX296
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1456)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1088)

if not cap.isOpened():
    print("❌ Lỗi: Không thể mở port camera!")
    exit()

# Raspberry Pi 5 cần vài khung hình đầu tiên để tự động cân bằng sáng (Warm-up)
print("Đang chờ Camera sưởi ấm (warm-up)...")
for i in range(10):
    ret, frame = cap.read()
    time.sleep(0.1)

if ret and frame is not None:
    print(f"✅ THÀNH CÔNG! Đã đọc được ảnh kích thước: {frame.shape}")
    cv2.imwrite("test_image.jpg", frame)
    print("Đã lưu ảnh thành file test_image.jpg. Hãy mở file này lên xem thử!")
else:
    print("❌ THẤT BẠI: Mở được port nhưng KHÔNG THỂ đọc được dữ liệu ảnh.")

cap.release()