# missions/rescue_round.py
class RescueMission:
    def __init__(self, commander, vision):
        self.commander = commander
        self.vision = vision

    def run_step(self):
        # Logic: 
        # 1. Tìm AruCo của điểm V1
        # 2. Hạ độ cao xuống < 0.5m để gắp
        # 3. Kích hoạt Servo gắp
        # 4. Bay lên lại độ cao an toàn
        pass