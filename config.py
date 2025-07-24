# config.py

import os
from dotenv import load_dotenv

# Tải tất cả các biến từ file .env vào môi trường
load_dotenv()

# --- BẮT BUỘC ---
# Lấy token từ biến môi trường, không hardcode ở đây nữa
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- TÙY CHỈNH (CÓ THỂ GIỮ NGUYÊN) ---
DB_NAME = "spx_tracking_data.db"
CHECK_INTERVAL_SECONDS = 900