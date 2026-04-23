# utils/logger.py
import time
import csv
import os

class FlightLogger:
    def __init__(self, folder="logs"):
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.filename = f"{folder}/flight_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        self.file = open(self.filename, mode='w', newline='')
        self.writer = csv.writer(self.file)
        # Header theo yêu cầu giám sát
        self.writer.writerow(['Timestamp', 'State', 'Alt', 'Battery', 'Vibration', 'Message'])

    def log(self, state, sensors_data, message=""):
        self.writer.writerow([
            time.time(),
            state,
            sensors_data.get('alt', 0),
            sensors_data.get('battery_v', 0),
            sensors_data.get('vibration_z', 0),
            message
        ])
        self.file.flush() # Đảm bảo dữ liệu được ghi ngay cả khi crash

    def close(self):
        self.file.close()