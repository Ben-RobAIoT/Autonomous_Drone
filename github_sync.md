Bước 1: Tạo file .gitignore (Cực kỳ quan trọng)
Mở Terminal trên Pi, đảm bảo bạn đang ở trong thư mục dự án (Drone-PBTin_ws), gõ lệnh sau để tạo file .gitignore và ghi các thư mục cần bỏ qua vào đó:

Bash
nano .gitignore
Dán nội dung này vào file:

Plaintext
# Bỏ qua môi trường ảo Python
venv/
env/

# Bỏ qua các file rác sinh ra trong quá trình chạy
__pycache__/
*.pyc
*.pyo

# Bỏ qua file log và ảnh test
logs/
*.csv
test_image.jpg
(Nhấn Ctrl+O -> Enter để lưu, sau đó Ctrl+X để thoát).

Bước 2: Đẩy code lần đầu lên GitHub
Vẫn tại Terminal trong thư mục dự án, bạn gõ lần lượt các lệnh sau:

Bash
# 1. Khởi tạo kho chứa Git tại máy của bạn
git init

# 2. Gom toàn bộ code (trừ những thứ trong .gitignore)
git add .

# 3. Đóng gói và dán nhãn cho lần lưu này
git commit -m "Initial commit: Hoàn thiện kiến trúc Modular OOP và Web GCS"

# 4. Đặt tên nhánh chính là 'main'
git branch -M main

# 5. Kết nối với kho chứa của bạn trên GitHub
git remote add origin https://github.com/Ben-RobAIoT/Autonomous_Drone.git

# 6. Đẩy toàn bộ code lên mạng
git push -u origin main
Lưu ý: Khi push, GitHub có thể yêu cầu Username và Mật khẩu. Hiện tại GitHub yêu cầu dùng Personal Access Token (PAT) thay cho mật khẩu thường. Nếu bạn chưa có Token, hãy vào GitHub > Settings > Developer settings > Personal access tokens (classic) để tạo một cái nhé.

Bước 3: Tạo file README.md (Bản hướng dẫn "Bỏ túi")
Hãy tạo một file tên là README.md ngay trong thư mục gốc của bạn. File này sẽ tự động hiển thị rất đẹp trên trang chủ GitHub. Tui đã viết sẵn cho bạn một bản siêu dễ hiểu:

Markdown
# 🚁 Dự án Autonomous Drone (UAV Contest 2026)

Hệ thống điều khiển Drone tự hành sử dụng Raspberry Pi 5, Pixhawk (PX4), và Camera nhận diện ảnh (OpenCV). Dự án được thiết kế theo kiến trúc **Modular OOP** kèm theo một **Web Dashboard GCS** tích hợp.

## 📁 Cấu trúc thư mục cốt lõi
- `main.py`: Trái tim của hệ thống, chạy tất cả các luồng (Web, Vision, Flight Control).
- `core/`: Xử lý kết nối MAVLink và State Machine.
- `sensors/`: Quản lý Lidar, Optical Flow, Battery và Pi HQ Camera.
- `control/`: Xử lý PID và gửi lệnh điều khiển bay.
- `dashboard/`: Giao diện Ground Control Station chạy trên trình duyệt.

---

## 🛠 Hướng dẫn Cài đặt & Chạy nhanh

**1. Kích hoạt môi trường ảo (Bắt buộc):**
```bash
source venv/bin/activate
(Nếu chưa cài thư viện, hãy chạy: pip install -r requirements.txt)

2. Khởi động Drone & Web GCS:

Bash
libcamerify python3 main.py
(Lưu ý: Phải dùng libcamerify nếu đang dùng luồng Camera trên Pi OS Bookworm).

3. Mở Bảng điều khiển:
Truy cập: http://<IP_CỦA_PI>:5000 trên trình duyệt máy tính hoặc điện thoại cùng mạng WiFi.

🔄 Cẩm nang đồng bộ Git (Dành cho Kỹ sư)
Để quá trình làm việc nhóm hoặc update code không bị lỗi, hãy nhớ thần chú: "Pull trước khi làm, Push sau khi xong".

1. Khi muốn LƯU code lên GitHub (Push)
Sau khi bạn code xong một tính năng và muốn lưu lại lên mạng:

Bash
git add .
git commit -m "Ghi chú tóm tắt tính năng vừa làm (VD: Fix lỗi Lidar)"
git push
2. Khi muốn LẤY code mới nhất từ GitHub về (Pull)
Nếu bạn (hoặc đồng đội) vừa sửa code trên GitHub và muốn kéo về máy tính Pi:

Bash
git pull origin main
3. Bí kíp xử lý lỗi
Quên thêm file vào .gitignore? Hãy xóa nó khỏi git cache: git rm -r --cached <tên_file>

Bị xung đột code (Conflict)? Đừng hoảng hốt. Gõ git status để xem file nào bị đỏ, mở file đó ra sửa lại bằng tay, sau đó git add và git commit lại.


Bạn chỉ cần tạo file `README.md`, dán nội dung trên vào, rồi chạy lại lệnh:
`git add README.md` -> `git commit -m "Thêm hướng dẫn README"` -> `git push` là xong! 

Repo của bạn trông sẽ cực kỳ "Pro" trong mắt ban giám khảo và đồng đội!