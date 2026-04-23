from pymavlink import mavutil
import time

# Kết nối
connection = mavutil.mavlink_connection('/dev/ttyAMA0', baud=115200)

print("Đang chờ Heartbeat...")
connection.wait_heartbeat()
print("Đã kết nối thành công!")

# --- BỔ SUNG ĐOẠN NÀY: Yêu cầu Pixhawk gửi dữ liệu ---
# MAV_DATA_STREAM_ALL = 0 (Yêu cầu tất cả các loại dữ liệu)
# 10 là tần số (Hz) - tức là 10 lần mỗi giây
connection.mav.request_data_stream_send(
    connection.target_system, 
    connection.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL, 
    10, 1
)

while True:
    try:
        # Không dùng blocking=True nữa để tránh bị treo nếu mất kết nối
        msg = connection.recv_match(type=['VFR_HUD', 'SYS_STATUS', 'ATTITUDE'], blocking=True, timeout=1.0)
        
        if not msg:
            print("Đang đợi dữ liệu...")
            continue
            
        m_type = msg.get_type()
        if m_type == 'VFR_HUD':
            print(f"Alt: {msg.alt}m | Speed: {msg.groundspeed}m/s")
        elif m_type == 'SYS_STATUS':
            print(f"Battery: {msg.voltage_battery/1000.0}V | {msg.battery_remaining}%")
        elif m_type == 'ATTITUDE':
            print(f"Roll: {round(msg.roll, 2)} | Pitch: {round(msg.pitch, 2)}")
            
    except KeyboardInterrupt:
        print("\nDừng test.")
        break