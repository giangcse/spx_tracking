# main.py

import logging
from telegram.ext import Application, CommandHandler

import config
import database as db
import bot_handlers as handlers

# Thiết lập logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

def main() -> None:
    """Hàm chính để khởi tạo và chạy bot."""
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("!!! LỖI: Vui lòng điền BOT_TOKEN vào file config.py.")
        return

    # 1. Kết nối và thiết lập database
    conn = db.get_db_connection()
    if conn:
        db.setup_database(conn)
    else:
        print("Không thể kết nối database, bot dừng lại.")
        return

    # 2. Khởi tạo Application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Lưu kết nối DB vào bot_data để các handler có thể truy cập
    application.bot_data['db_connection'] = conn

    # 3. Đăng ký các command handler
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("track", handlers.track))
    application.add_handler(CommandHandler("untrack", handlers.untrack))
    application.add_handler(CommandHandler("list", handlers.list_tracked))
    application.add_handler(CommandHandler("status", handlers.status_now))
    application.add_handler(CommandHandler("history", handlers.history))
    
    # 4. Thiết lập và chạy Job Queue để kiểm tra định kỳ
    job_queue = application.job_queue
    job_queue.run_repeating(handlers.check_for_updates, interval=config.CHECK_INTERVAL_SECONDS, first=10)
    
    # 5. Chạy bot
    print("Bot đang chạy... Nhấn Ctrl+C để dừng.")
    application.run_polling()
    
    # Đóng kết nối DB khi bot dừng
    conn.close()
    print("Đã đóng kết nối database.")

if __name__ == '__main__':
    main()