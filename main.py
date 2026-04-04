from pymavlink import mavutil
import time
import threading

class DroneAutoPilot:
    DEFAULT_CONFIG = {
        # Flight target
        'hover_target_alt_m': 1.7,

        # Throttle bounds
        'hover_throttle': 1300,
        'disarm_throttle': 1000,
        'max_throttle': 1600,

        # Altitude controller (PID)
        'control_loop_hz': 20.0,
        'altitude_kp': 120.0,
        'altitude_ki': 20.0,
        'altitude_kd': 45.0,
        'integral_limit': 1.0,

        # Profile rates (m/s)
        'takeoff_ascent_rate_mps': 0.35,
        'landing_descent_rate_mps': 0.25,
        'landing_slow_zone_alt_m': 0.35,
        'landing_slow_descent_rate_mps': 0.12,
        'landing_stop_alt_m': 0.35,
    }

    def __init__(self, port='/dev/ttyAMA0', baud=115200, config=None):
        print("Đang kết nối với Pixhawk...")
        self.connection = mavutil.mavlink_connection(port, baud=baud)
        self.connection.wait_heartbeat()
        print("Đã kết nối!")

        self.config = dict(self.DEFAULT_CONFIG)
        if config:
            self.config.update(config)
        
        # Biến toàn cục lưu trạng thái drone
        self.current_alt = 0.0
        self.is_running = True
        self.base_throttle = self.config['hover_throttle']
        self.min_throttle = self.config['disarm_throttle']
        self.max_throttle = self.config['max_throttle']

        # Trạng thái cho bộ điều khiển độ cao
        self._alt_integral = 0.0
        self._prev_alt = 0.0
        
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

    def _compute_altitude_throttle(self, target_alt, dt):
        """Tính PWM dựa trên độ cao mục tiêu và độ cao hiện tại."""
        error = target_alt - self.current_alt

        # Integral chống trôi: giới hạn tích lũy sai số.
        self._alt_integral += error * dt
        i_limit = self.config['integral_limit']
        self._alt_integral = max(-i_limit, min(i_limit, self._alt_integral))

        # D term dùng vận tốc theo trục Z tính từ biến thiên độ cao.
        vertical_speed = (self.current_alt - self._prev_alt) / dt if dt > 0 else 0.0
        self._prev_alt = self.current_alt

        kp = self.config['altitude_kp']
        ki = self.config['altitude_ki']
        kd = self.config['altitude_kd']
        correction = (kp * error) + (ki * self._alt_integral) - (kd * vertical_speed)

        throttle = int(self.base_throttle + correction)
        return max(self.min_throttle, min(self.max_throttle, throttle))

    def arm_drone(self):
        print("\n--- CHUẨN BỊ CẤT CÁNH ---")
        self.connection.mav.set_mode_send(self.connection.target_system, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 0) # Mode STABILIZE
        time.sleep(1)
        self.connection.mav.command_long_send(self.connection.target_system, self.connection.target_component, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 21196, 0, 0, 0, 0, 0)
        time.sleep(2)
        print("Đã Arm!")

    def disarm_drone(self):
        print("\n--- ĐANG KHÓA ĐỘNG CƠ ---")
        self.set_throttle(self.min_throttle)
        self.connection.mav.command_long_send(self.connection.target_system, self.connection.target_component, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0)
        self.connection.mav.rc_channels_override_send(self.connection.target_system, self.connection.target_component, 0, 0, 0, 0, 0, 0, 0, 0)

    def takeoff(self, target_alt):
        print(f"\n[TAKEOFF] Đang nâng độ cao lên {target_alt}m...")
        dt = 1.0 / self.config['control_loop_hz']
        start_alt = self.current_alt
        commanded_alt = start_alt

        # Tăng target độ cao theo tốc độ m/s; PWM luôn tính theo sai số độ cao.
        while self.current_alt < target_alt - 0.03:
            commanded_alt += self.config['takeoff_ascent_rate_mps'] * dt
            commanded_alt = min(target_alt, commanded_alt)

            throttle = self._compute_altitude_throttle(commanded_alt, dt)
            self.set_throttle(throttle)
            self.send_heartbeat()
            print(f"Cao độ: {self.current_alt:.2f}m | Target: {commanded_alt:.2f}m | Ga: {throttle}", end='\r')
            time.sleep(dt)
        
        print(f"\n[TAKEOFF] Đã đạt độ cao {target_alt}m!")

    def hold_altitude(self, target_alt=None):
        if target_alt is None:
            target_alt = self.config['hover_target_alt_m']

        print(f"\n[HOLD] Giữ độ cao {target_alt}m... (Nhấn Ctrl+C để Hạ cánh)")
        dt = 1.0 / self.config['control_loop_hz']
        while True:
            throttle = self._compute_altitude_throttle(target_alt, dt)
            self.set_throttle(throttle)
            self.send_heartbeat()
            print(f"Cao độ thực tế: {self.current_alt:.2f}m | Target: {target_alt:.2f}m | Ga: {throttle}", end='\r')
            time.sleep(dt)

    def land(self):
        print("\n[LANDING] Đang hạ cánh từ từ...")
        dt = 1.0 / self.config['control_loop_hz']
        commanded_alt = self.current_alt
        stop_alt = self.config['landing_stop_alt_m']
        slow_zone_alt = self.config['landing_slow_zone_alt_m']
        
        # Hạ target độ cao theo profile; PWM được tính từ sai số độ cao.
        while self.current_alt > stop_alt:
            if self.current_alt > slow_zone_alt:
                descent_rate = self.config['landing_descent_rate_mps']
            else:
                descent_rate = self.config['landing_slow_descent_rate_mps']

            commanded_alt -= descent_rate * dt
            commanded_alt = max(stop_alt, commanded_alt)

            throttle = self._compute_altitude_throttle(commanded_alt, dt)
            
            self.set_throttle(throttle)
            self.send_heartbeat()
            print(f"Cao độ: {self.current_alt:.2f}m | Target: {commanded_alt:.2f}m | Ga: {throttle}", end='\r')
            time.sleep(dt)

        # Giữ ga thấp khi gần mặt đất trước khi disarm.
        self.set_throttle(self.min_throttle)
        self.send_heartbeat()
                
        print(f"\n[LANDING] Đã về gần mặt đất (<= {stop_alt}m), chuẩn bị khóa động cơ.")

# ==========================================
# PHẦN CHẠY CHÍNH (MAIN BLOCK)
# ==========================================
if __name__ == '__main__':
    COMMON_CONFIG = {
        # Chỉ override những tham số bạn muốn đổi so với DEFAULT_CONFIG.
        'hover_target_alt_m': 1.6,
        'landing_stop_alt_m': 0.4,
    }

    active_config = dict(DroneAutoPilot.DEFAULT_CONFIG)
    active_config.update(COMMON_CONFIG)

    drone = DroneAutoPilot(config=active_config)
    landed_safely = False

    print(
        f"[CONFIG] hover_target_alt_m={drone.config['hover_target_alt_m']} | "
        f"landing_stop_alt_m={drone.config['landing_stop_alt_m']}"
    )
    
    try:
        input("Nhấn ENTER để Arm và Cất cánh...")
        drone.arm_drone()
        
        # 1. Cất cánh lên 1.6 mét
        drone.takeoff(target_alt=drone.config['hover_target_alt_m'])
        
        # 2. Giữ độ cao ở hover_target_alt_m (kết thúc bằng Ctrl+C)
        drone.hold_altitude()
        
        # 3. Quá trình này tự động chạy khi bạn bấm Ctrl+C ở bước 2
        drone.land()
        landed_safely = True
        
    except KeyboardInterrupt:
        print("\n[MAIN] Nhận Ctrl+C! Thực hiện hạ cánh an toàn...")
        if drone.current_alt > drone.config['landing_stop_alt_m']:
            drone.land()
            landed_safely = True
        else:
            print("[MAIN] Drone đã gần mặt đất, tiến hành khóa động cơ.")
        
    finally:
        # Luôn luôn khóa động cơ khi kết thúc hoặc có lỗi
        if not landed_safely and drone.current_alt > drone.config['landing_stop_alt_m']:
            print("\n[MAIN] Phát hiện chưa hạ cánh, thử hạ cánh an toàn trước khi disarm...")
            drone.land()
        drone.disarm_drone()
        drone.is_running = False