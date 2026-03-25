from pymavlink import mavutil
import time

# 1. Kết nối
connection = mavutil.mavlink_connection('/dev/ttyAMA0', baud=115200)
connection.wait_heartbeat()
print("Đã kết nối! Đang cấu hình luồng dữ liệu...")

# 2. Yêu cầu các Message ID cần thiết
def request_message_interval(message_id, frequency_hz):
    """Yêu cầu Pixhawk gửi một loại tin nhắn cụ thể với tần số Hz"""
    connection.mav.command_long_send(
        connection.target_system, connection.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
        message_id, # ID tin nhắn
        int(1e6 / frequency_hz), # Khoảng cách thời gian (microseconds)
        0, 0, 0, 0, 0
    )

# Yêu cầu: Distance Sensor (132), VFR_HUD (74), Vibration (241), Optical Flow (100)
messages = [132, 74, 241, 100]
for msg_id in messages:
    request_message_interval(msg_id, 10) # 10Hz là đủ để theo dõi

print("--- HỆ THỐNG GIÁM SÁT ĐỘ CAO TOÀN DIỆN ---")

try:
    while True:
        msg = connection.recv_match(blocking=True, timeout=1)
        if not msg: continue

        msg_type = msg.get_type()

        # A. ĐỘ CAO THẬT (Từ Rangefinder/Lidar)
        if msg_type == 'DISTANCE_SENSOR':
            # current_distance (cm), min_distance (cm), max_distance (cm)
            alt_rf = msg.current_distance / 100.0
            print(f"[RANGEFINDER] Cao: {alt_rf}m | Giới hạn: {msg.min_distance/100}m - {msg.max_distance/100}m")
            # Kiểm tra nếu drone bay quá cao vượt ngưỡng max của cảm biến
            if msg.current_distance >= msg.max_distance:
                print(" > CẢNH BÁO: Vượt ngưỡng Max! Dữ liệu không còn tin cậy.")

        # B. ĐỘ CAO TỔNG HỢP & MÔI TRƯỜNG (Từ Baro + EKF)
        elif msg_type == 'VFR_HUD':
            # alt: Độ cao so với mực nước biển hoặc điểm takeoff (m)
            # climb: Tốc độ leo cao (m/s) - cực quan trọng để biết drone đang vọt lên hay rơi
            print(f"[HUD/BARO] Cao EKF: {msg.alt}m | Tốc độ leo: {msg.climb}m/s")

        # C. ẢNH HƯỞNG RUNG ĐỘNG (Nguyên nhân gây nhiễu cảm biến)
        elif msg_type == 'VIBRATION':
            # Rung động lớn (>30) sẽ làm cảm biến Optical Flow và Lidar bị sai lệch
            print(f"[RUNG ĐỘNG] X: {round(msg.vibration_x, 2)} | Y: {round(msg.vibration_y, 2)} | Z: {round(msg.vibration_z, 2)}")
            if msg.vibration_z > 30:
                print(" > CẢNH BÁO: Máy bay rung quá mạnh! Cao độ sẽ bị nhiễu.")

        # D. CHẤT LƯỢNG MÔI TRƯỜNG (Từ Optical Flow)
        elif msg_type == 'OPTICAL_FLOW_RAD':
            # quality: 0 (tệ) - 255 (tốt). Nếu dưới 100, đừng bay tự động.
            print(f"[OPTICAL FLOW] Chất lượng bề mặt đất: {msg.quality}/255")
            if msg.quality < 80:
                print(" > CẢNH BÁO: Ánh sáng yếu hoặc bề mặt đất không rõ ràng.")

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Dừng giám sát.")