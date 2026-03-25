from pymavlink import mavutil
import time
import threading

class DroneAutoPilot:
    def __init__(self, port='/dev/ttyAMA0', baud=115200):
        print("Đang kết nối với Pixhawk...")
        self.connection = mavutil.mavlink_connection(port, baud=baud)
        self.connection.wait_heartbeat()
        print("Đã kết nối!")
        
        # Biến toàn cục lưu trạng thái drone
        self.current_alt = 0.0
        self.is_running = True
        self.base_throttle = 1300 # Mức ga lơ lửng (Hover throttle) - Tùy chỉnh theo drone thật
        
        # Yêu cầu dữ liệu Rangefinder
        self.connection.mav.command_long_send(
            self.connection.target_system, self.connection.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0, 132, 100000, 0, 0, 0, 0, 0)
            
        # Bắt đầu luồng đọc dữ liệu ngầm
        self.telemetry_thread = threading.Thread(target=self._read_telemetry_loop)
        self.telemetry_thread.daemon = True
        self.telemetry_thread.start()

    def _read_telemetry_loop(self):
        """Luồng chạy ngầm để liên tục cập nhật độ cao"""
        while self.is_running:
            msg = self.connection.recv_match(type='DISTANCE_SENSOR', blocking=False)
            if msg:
                self.current_alt = msg.current_distance / 100.0
            time.sleep(0.02) # Đọc ở 50Hz

    def send_heartbeat(self):
        self.connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)

    def set_throttle(self, pwm):
        """Gửi mức ga vào kênh 3"""
        self.connection.mav.rc_channels_override_send(
            self.connection.target_system, self.connection.target_component,
            65535, 65535, pwm, 65535, 65535, 65535, 65535, 65535)

    def arm_drone(self):
        print("\n--- CHUẨN BỊ CẤT CÁNH ---")
        self.connection.mav.set_mode_send(self.connection.target_system, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 0) # Mode STABILIZE
        time.sleep(1)
        self.connection.mav.command_long_send(self.connection.target_system, self.connection.target_component, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 21196, 0, 0, 0, 0, 0)
        time.sleep(2)
        print("Đã Arm!")

    def disarm_drone(self):
        print("\n--- ĐANG KHÓA ĐỘNG CƠ ---")
        self.set_throttle(900)
        self.connection.mav.command_long_send(self.connection.target_system, self.connection.target_component, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0)
        self.connection.mav.rc_channels_override_send(self.connection.target_system, self.connection.target_component, 0, 0, 0, 0, 0, 0, 0, 0)

    def takeoff(self, target_alt):
        print(f"\n[TAKEOFF] Đang nâng độ cao lên {target_alt}m...")
        current_throttle = 1100
        
        # Tăng ga từ từ cho đến khi đạt độ cao mong muốn
        while self.current_alt < target_alt:
            if current_throttle < self.base_throttle + 150: # Giới hạn mức ga tối đa để tránh vọt quá nhanh
                current_throttle += 5 # Tăng ga từ từ
            
            self.set_throttle(current_throttle)
            self.send_heartbeat()
            print(f"Cao độ: {self.current_alt}m | Ga: {current_throttle}", end='\r')
            time.sleep(0.1)
        
        print(f"\n[TAKEOFF] Đã đạt độ cao {target_alt}m!")

    def hold_altitude(self, target_alt):
        print("\n[HOLD] Đang giữ độ cao... (Nhấn Ctrl+C để Hạ cánh)")
        try:
            while True:
                # Logic PID tối giản (P-Controller)
                error = target_alt - self.current_alt
                
                # Tính toán mức ga bù trừ dựa trên sai số độ cao
                # Nếu drone thấp hơn target -> error dương -> tăng ga
                # Nếu drone cao hơn target -> error âm -> giảm ga
                adjustment = int(error * 100) 
                
                # Giới hạn mức ga để không vọt quá nhanh hoặc rớt quá lẹ
                throttle = self.base_throttle + adjustment
                throttle = max(1100, min(1600, throttle)) 
                
                self.set_throttle(throttle)
                self.send_heartbeat()
                print(f"Cao độ thực tế: {self.current_alt}m | Ga đang bù: {throttle}", end='\r')
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n[HOLD] Nhận lệnh dừng! Chuyển sang hạ cánh...")

    def land(self):
        print("\n[LANDING] Đang hạ cánh từ từ...")
        current_throttle = self.base_throttle
        
        # Hạ ga từ từ cho đến khi chạm đất (ví dụ ngưỡng min là 0.35m)
        while self.current_alt > 0.6:
            current_throttle -= 5 # Giảm ga từ từ
            current_throttle = max(1000, current_throttle) # Không tụt dưới 1000
            
            self.set_throttle(current_throttle)
            self.send_heartbeat()
            print(f"Cao độ: {self.current_alt}m | Ga: {current_throttle}", end='\r')
            time.sleep(0.1)
            
            # Nếu ga đã về min mà vẫn chưa chạm đất (ví dụ bị kẹt), ép thoát vòng lặp
            if current_throttle <= 1000:
                break
                
        print("\n[LANDING] Đã chạm đất an toàn!")

# ==========================================
# PHẦN CHẠY CHÍNH (MAIN BLOCK)
# ==========================================
if __name__ == '__main__':
    drone = DroneAutoPilot()
    
    try:
        input("Nhấn ENTER để Arm và Cất cánh...")
        drone.arm_drone()
        
        # 1. Cất cánh lên 1.0 mét
        drone.takeoff(target_alt=1.0)
        
        # 2. Giữ độ cao ở 1.0 mét (Nó sẽ kẹt ở đây cho đến khi bạn bấm Ctrl+C)
        drone.hold_altitude(target_alt=1.0)
        
        # 3. Quá trình này tự động chạy khi bạn bấm Ctrl+C ở bước 2
        drone.land()
        
    finally:
        # Luôn luôn khóa động cơ khi kết thúc hoặc có lỗi
        drone.disarm_drone()
        drone.is_running = False