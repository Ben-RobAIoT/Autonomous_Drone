# sensors/monitor.py
from pymavlink import mavutil
import threading
import time

class SensorManager:
    def __init__(self, connection):
        self.conn = connection.master
        self.is_running = True
        
        # Kho dữ liệu
        self.data = {
            'alt': 0.0,
            'flow_qual': 0,
            'vibration_z': 0.0,
            'battery_v': 0.0
        }

        self._request_streams()
        
        # Chạy luồng đọc ngầm
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def _request_streams(self):
        """Yêu cầu Pixhawk gửi data"""
        # DISTANCE_SENSOR (132), OPTICAL_FLOW_RAD (100), VIBRATION (241), SYS_STATUS (1)
        for msg_id in [132, 100, 241, 1]:
            self.conn.mav.command_long_send(
                self.conn.target_system, self.conn.target_component,
                mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
                msg_id, 100000, 0, 0, 0, 0, 0) # 10Hz

    def _read_loop(self):
        while self.is_running:
            msg = self.conn.recv_match(blocking=False)
            if not msg:
                time.sleep(0.01)
                continue
                
            m_type = msg.get_type()
            if m_type == 'DISTANCE_SENSOR':
                self.data['alt'] = msg.current_distance / 100.0
            elif m_type == 'OPTICAL_FLOW_RAD':
                self.data['flow_qual'] = msg.quality
            elif m_type == 'VIBRATION':
                self.data['vibration_z'] = msg.vibration_z
            elif m_type == 'SYS_STATUS':
                self.data['battery_v'] = msg.voltage_battery / 1000.0

    def get_altitude(self):
        return self.data['alt']
    
    def get_all(self):
        return self.data

    def stop(self):
        self.is_running = False