# sensors/vision.py
import cv2
import threading
import time
import subprocess

class VisionManager:
    def __init__(self):
        print("[VISION] 1. Đang khởi tạo Camera Server nội bộ...")
        
        # Bật rpicam-vid để phát stream MJPEG nội bộ qua cổng 8888
        cmd = [
            "rpicam-vid",
            "-t", "0",
            "--nopreview",
            "--codec", "mjpeg",      # Dùng MJPEG để OpenCV dễ đọc nhất
            "--width", "640",
            "--height", "480",
            "--framerate", "20",
            "--listen",              # Lắng nghe kết nối
            "-o", "tcp://127.0.0.1:8888"
        ]
        # Chạy ngầm tiến trình này
        self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Phải đợi khoảng 2-3 giây để Camera Server khởi động xong
        print("[VISION] Đang chờ ống kính mở (3s)...")
        time.sleep(3) 
        
        print("[VISION] 2. OpenCV đang kết nối vào luồng Camera...")
        # Đọc dữ liệu từ luồng TCP nội bộ thay vì đọc phần cứng /dev/video0
        self.cap = cv2.VideoCapture("tcp://127.0.0.1:8888")
        
        self.frame = None
        self.is_running = True
        
        # Khởi động luồng đọc ảnh
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        frames_read = 0
        while self.is_running:
            success, image = self.cap.read()
            if success and image is not None:
                self.frame = image
                frames_read += 1
                if frames_read == 1:
                    print("\\n[VISION] TADA! ĐÃ BẮT ĐƯỢC KHUNG HÌNH ĐẦU TIÊN! 📸\\n")
            else:
                # Nếu mất khung hình, thử kết nối lại hoặc đợi
                time.sleep(0.1)

    def get_encoded_frame(self):
        if self.frame is None: 
            return None
        try:
            success, jpeg = cv2.imencode('.jpg', self.frame)
            if success: 
                return jpeg.tobytes()
        except Exception as e:
            pass
        return None

    def stop(self):
        self.is_running = False
        if hasattr(self, 'cap'):
            self.cap.release()
        if self.process:
            self.process.terminate()
            self.process.wait()
        print("[VISION] Đã tắt Camera Server.")