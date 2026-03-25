from pymavlink import mavutil
import time

# 1. Kết nối (Sửa cổng nếu bạn dùng USB hoặc GPIO)
connection = mavutil.mavlink_connection('/dev/ttyAMA0', baud=115200)

print("Đang chờ Heartbeat...")
connection.wait_heartbeat()
print("Đã kết nối!")

# 2. Yêu cầu truyền dữ liệu khoảng cách (Distance Sensor)
# MAV_DATA_STREAM_EXTRA2 thường chứa các dữ liệu cảm biến bổ sung
# Yêu cầu Pixhawk gửi tin nhắn DISTANCE_SENSOR (ID số 132)
# 500000 là micro giây (tương đương 2Hz - 2 lần mỗi giây)
connection.mav.command_long_send(
    connection.target_system,
    connection.target_component,
    mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
    0,
    132,    # Message ID của DISTANCE_SENSOR
    500000, # Interval tính bằng microseconds
    0, 0, 0, 0, 0
)
print("Đã gửi lệnh yêu cầu DISTANCE_SENSOR...")

print("--- Đang đọc độ cao từ Optical Flow ---")

try:
    while True:
        # Tìm tin nhắn DISTANCE_SENSOR
        msg = connection.recv_match(type='DISTANCE_SENSOR', blocking=True, timeout=1)
        
        if msg:
            # current_distance tính bằng cm, chia 100 để ra mét
            altitude_m = msg.current_distance / 100.0
            print(f"Độ cao hiện tại: {altitude_m} m (Min: {msg.min_distance/100}m, Max: {msg.max_distance/100}m)")
        else:
            # Nếu không có DISTANCE_SENSOR, thử đọc từ VFR_HUD (độ cao tổng hợp)
            msg_hud = connection.recv_match(type='VFR_HUD', blocking=False)
            if msg_hud:
                print(f"Độ cao tổng hợp (HUD): {msg_hud.alt} m")
            else:
                print("Đang đợi dữ liệu từ cảm biến...")
        
        time.sleep(0.2)

except KeyboardInterrupt:
    print("Dừng đọc dữ liệu.")