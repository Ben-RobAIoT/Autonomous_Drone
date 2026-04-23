# core/connection.py
from pymavlink import mavutil
import time

class DroneConnection:
    def __init__(self, port, baud):
        print(f"[CONNECTION] Đang kết nối tới {port}...")
        self.master = mavutil.mavlink_connection(port, baud=baud)
        self.master.wait_heartbeat()
        print(f"[CONNECTION] Đã kết nối! Target System: {self.master.target_system}")

    def send_heartbeat(self):
        self.master.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_GCS,
            mavutil.mavlink.MAV_AUTOPILOT_INVALID, 
            0, 0, 0
        )

    def set_mode(self, mode_name):
        mode_id = self.master.mode_mapping().get(mode_name)
        if mode_id is None:
            print(f"[ERROR] Chế độ {mode_name} không hợp lệ!")
            return False
        
        self.master.mav.set_mode_send(
            self.master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id
        )
        print(f"[CONNECTION] Đã chuyển sang mode: {mode_name}")
        return True