# Dockerfile

# 1. Chọn một image Python nhẹ và chính thức làm nền
FROM python:3.11-slim

# 2. Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# 3. Sao chép file requirements vào trước để tận dụng cache của Docker
# Nếu file này không đổi, Docker sẽ không cần cài lại thư viện ở những lần build sau
COPY requirements.txt .

# 4. Cài đặt các thư viện Python cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# 5. Sao chép toàn bộ mã nguồn của dự án vào thư mục làm việc
COPY . .

# 6. Lệnh sẽ được thực thi khi container khởi chạy
CMD ["python", "main.py"]