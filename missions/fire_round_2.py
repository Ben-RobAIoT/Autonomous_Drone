# missions/fire_round.py
class FireMission:
    def __init__(self, commander, vision):
        self.commander = commander
        self.vision = vision
        self.targets = ["F1", "F2", "F3", "F4", "F5"]

    def run_step(self, current_alt):
        # Logic:
        # 1. Nhận diện khối màu đỏ bằng OpenCV (vision.py)
        # 2. Điều chỉnh vị trí X, Y sao cho tâm khối đỏ trùng tâm camera
        # 3. Nếu ổn định ở độ cao > 3.0m (Luật thi) -> Kích hoạt Servo thả bóng
        pass