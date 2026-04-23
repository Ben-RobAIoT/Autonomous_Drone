# config.py

class SystemConfig:
    PORT = '/dev/ttyAMA0'
    BAUD = 115200

class FlightConfig:
    HOVER_TARGET_ALT = 1.7      # Độ cao thi đấu (mét)
    LANDING_STOP_ALT = 0.3      # Độ cao ngắt động cơ (mét)
    LOOP_HZ = 20.0              # Tần số vòng lặp điều khiển chính (20Hz)
    
class PIDConfig:
    # Thông số cho bộ PID tự chế (nếu không dùng PID nội bộ của Pixhawk)
    ALT_KP = 150
    ALT_KI = 20
    ALT_KD = 5
    PWM_MIN = 1350
    PWM_MAX = 1900
    PWM_HOVER = 1500