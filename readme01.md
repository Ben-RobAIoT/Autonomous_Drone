git init
git add .
git config --global user.email "beniot.robaiot1137@gmail.com"
git config --global user.name "Beniot_Phan"  
git branch -M main
git commit -m "name_git"
git push -u origin main

=====================================
🏁 Quy trình Push Code "Chuẩn Pro"
Sau khi bạn đã cấu hình danh tính (user.email, user.name) xong, từ giờ mỗi khi bạn sửa code, bạn chỉ cần làm 3 lệnh này:

1. Gom hàng (git add)
Lệnh này giúp bạn chọn những thay đổi nào muốn đưa vào "gói hàng" để gửi đi.

Lệnh: git add . (Dấu chấm nghĩa là chọn tất cả thay đổi trong thư mục).

2. Đóng gói (git commit)
Lệnh này giống như việc bạn dán nhãn lên gói hàng, ghi chú xem trong đó có gì mới.

Lệnh: git commit -m "Nội dung ghi chú"

Ví dụ: git commit -m "Thêm hàm takeoff và land"

3. Gửi đi (git push)
Đẩy "gói hàng" từ máy Pi 5 lên máy chủ GitHub.

Lệnh: git push

(Vì nãy bạn đã dùng -u origin main rồi nên giờ chỉ cần gõ git push là nó tự hiểu).

🛠 Những lưu ý "sống còn" để không bị lỗi
⚠️ Luôn dùng .gitignore
Trước khi git add ., hãy chắc chắn bạn có file .gitignore. Nếu không, Git sẽ gom cả nghìn file rác trong thư mục venv/ hoặc __pycache__/ lên mạng, làm kho code của bạn cực nặng và rối.

🔄 Quy trình "Sáng Pull - Chiều Push"
Nếu bạn làm việc nhóm hoặc dùng cả Laptop và Pi để code chung 1 dự án:

Sáng (trước khi bắt đầu code): Gõ git pull để tải những gì mới nhất từ GitHub về máy.

Chiều (sau khi code xong): Gõ add -> commit -> push để đẩy lên lại.

💡 Cách xem lại thành quả
Để kiểm tra xem mình đã lưu những gì, bạn có thể gõ:

git log --oneline: Xem danh sách các lần commit ngắn gọn.

git status: Xem hiện tại có file nào mới sửa mà chưa add không.