# control/commander.py
from pymavlink import mavutil
import time

class FlightCommander:
    def __init__(self, connection):
        self.conn = connection.master
        self.connection_obj = connection

    def arm(self):
        print("\n[COMMANDER] Đang Arm động cơ...")
        self.connection_obj.set_mode('ALT_HOLD') # Bắt buộc dùng ALT_HOLD cho an toàn
        time.sleep(0.5)
        self.conn.mav.command_long_send(
            self.conn.target_system, self.conn.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 21196, 0, 0, 0, 0, 0)
        time.sleep(2)

    def disarm(self):
        print("\n[COMMANDER] Đang Disarm động cơ...")
        self.conn.mav.command_long_send(
            self.conn.target_system, self.conn.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0)

    def set_rc_throttle(self, pwm):
        """Gắn mức ga ảo vào kênh 3"""
        self.conn.mav.rc_channels_override_send(
            self.conn.target_system, self.conn.target_component,
            65535, 65535, int(pwm), 65535, 65535, 65535, 65535, 65535)
            
    def land_safely(self):
        """Kích hoạt chế độ LAND của chính Pixhawk"""
        print("\n[COMMANDER] Kích hoạt LAND mode tự động...")
        self.connection_obj.set_mode('LAND')