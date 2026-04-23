from pymavlink import mavutil
import time

# 1. Kết nối (Đảm bảo dây TX/RX cắm đúng vào /dev/ttyAMA0 trên Pi 5)
connection = mavutil.mavlink_connection('/dev/ttyAMA0', baud=115200)
print("Đang chờ Heartbeat từ Pixhawk...")
connection.wait_heartbeat()
print(f"Đã kết nối thành công! System: {connection.target_system}")

def send_heartbeat():
    """Gửi Heartbeat định kỳ để Pixhawk biết Pi vẫn đang kết nối"""
    connection.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_GCS,
        mavutil.mavlink.MAV_AUTOPILOT_INVALID, 
        0, 0, 0)

def set_rc_channel_pwm(channel, pwm=1500):
    """Gửi lệnh điều khiển kênh RC (Kênh 3 là ga)"""
    channels = [65535] * 8
    if 1 <= channel <= 8:
        channels[channel - 1] = pwm
    connection.mav.rc_channels_override_send(
        connection.target_system,
        connection.target_component,
        *channels
    )

# --- BƯỚC 1: CHUYỂN SANG MODE STABILIZE ---
# Vì log của bạn báo 'Guided mode not armable' (do thiếu GPS/Home)
# Chuyển về Stabilize (Mode 0) là cách nhanh nhất để test động cơ.
print("Chuyển sang mode STABILIZE...")
connection.mav.set_mode_send(
    connection.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    0) # 0 = STABILIZE

# --- BƯỚC 2: GỬI LỆNH ARM ÉP BUỘC ---
print("Đang ép Arm động cơ (Force Arm)...")
connection.mav.command_long_send(
    connection.target_system,
    connection.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 
    1,      # 1 = Arm
    21196,  # Tham số Force Arm để bỏ qua các lỗi nhỏ
    0, 0, 0, 0, 0
)

# --- BƯỚC 3: KIỂM TRA TRẠNG THÁI ARM ---
start_time = time.time()
is_armed = False
while time.time() - start_time < 5:
    send_heartbeat()
    msg = connection.recv_match(type='HEARTBEAT', blocking=True, timeout=1)
    if msg and (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED):
        print("--- XÁC NHẬN: ĐỘNG CƠ ĐÃ MỞ KHÓA (ARMED) ---")
        is_armed = True
        break
    print("Đang chờ xác nhận Arm từ Pixhawk...")
    time.sleep(0.5)

# --- BƯỚC 4: CHẠY ĐỘNG CƠ VÀ DUY TRÌ TÍN HIỆU ---
if is_armed:
    try:
        print("Bắt đầu quay động cơ (15% ga). Nhấn Ctrl+C để dừng.")
        # Dùng vòng lặp while để "nuôi" tín hiệu ga liên tục
        while True:
            # Gửi ga 1150 (khoảng 15%) vào kênh 3
            set_rc_channel_pwm(3, 1000)
            
            # Gửi Heartbeat để không bị Fail-safe ngắt động cơ
            send_heartbeat()
            
            # Đọc phản hồi từ Pixhawk để tránh tràn bộ đệm
            connection.recv_msg()
            
            time.sleep(0.05) # Tần số 20Hz (mượt mà)

    except KeyboardInterrupt:
        print("\nĐang dừng khẩn cấp và khóa động cơ...")
        # Hạ ga về mức tối thiểu
        set_rc_channel_pwm(3, 1000)
        time.sleep(0.5)
        # Disarm
        connection.mav.command_long_send(
            connection.target_system, connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0)
        print("Đã Disarm an toàn.")
else:
    print("Không thể Arm. Hãy kiểm tra lại nút Safety Switch hoặc lỗi trên Mission Planner.")