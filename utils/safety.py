# utils/safety.py
class SafetyManager:
    def __init__(self, commander, sensors):
        self.commander = commander
        self.sensors = sensors
        self.is_failsafe_active = False

    def check_all(self):
        data = self.sensors.get_all()
        
        # 1. Kiểm tra Pin (Giả sử < 10.5V là nguy hiểm)
        if data['battery_v'] < 10.5 and data['battery_v'] > 5.0:
            print("[SAFETY] Pin yếu! Kích hoạt Failsafe...")
            return self.trigger_failsafe("LOW_BATTERY")

        # 2. Kiểm tra độ rung (Nhiễu cảm biến)
        if data['vibration_z'] > 60:
            print("[SAFETY] Rung quá mạnh! Hạ cánh an toàn...")
            return self.trigger_failsafe("HIGH_VIBRATION")

        # 3. Kiểm tra Optical Flow (Dành cho bay không GPS)
        if data['flow_qual'] < 10:
            print("[SAFETY] Mất dấu bề mặt! Giữ nguyên vị trí...")
            # Có thể chuyển sang ALT_HOLD thay vì hạ cánh ngay
            
        return True

    def trigger_failsafe(self, reason):
        if not self.is_failsafe_active:
            self.is_failsafe_active = True
            self.commander.land_safely()
            return False
        return True