# core/state_machine.py
from enum import Enum

class FlightState(Enum):
    IDLE = 0            # Chờ lệnh
    ARMING = 1          # Đang mở khóa
    TAKEOFF = 2         # Đang cất cánh
    MISSION_ACTIVE = 3  # Đang thực hiện nhiệm vụ (Vòng 1 hoặc 2)
    RETURN_LAND = 4     # Trở về và hạ cánh
    FAILSAFE = 5        # Sự cố khẩn cấp
    DISARMED = 6        # Đã khóa động cơ