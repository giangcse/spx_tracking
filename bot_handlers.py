# bot_handlers.py

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging

import database as db
import spx_service

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Chào {user_name} 👋\n\n"
        "Tôi là bot theo dõi đơn hàng Shopee Express\.\n"
        "Sử dụng các lệnh sau:\n"
        "`/track <mã>` \- Bắt đầu theo dõi\.\n"
        "`/untrack <mã>` \- Ngừng theo dõi\.\n"
        "`/status <mã>` \- Xem trạng thái mới nhất\.\n"
        "`/history <mã>` \- Xem toàn bộ lịch sử đơn\.\n"
        "`/list` \- Xem danh sách đang theo dõi\.",
        parse_mode=ParseMode.MARKDOWN_V2)

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    if not context.args:
        await update.message.reply_text("Vui lòng nhập mã vận đơn\. \nVí dụ: `/track SPXVN0123456789`", parse_mode=ParseMode.MARKDOWN_V2)
        return

    tracking_code = context.args[0].upper()
    conn = context.bot_data['db_connection']
    
    if db.get_tracked_order(conn, chat_id, tracking_code):
        await update.message.reply_text(f"Mã `{tracking_code}` đã có trong danh sách theo dõi của bạn\.", parse_mode=ParseMode.MARKDOWN_V2)
        return

    data = spx_service.fetch_spx_data(tracking_code)
    if not data or data.get("retcode") != 0 or not data.get("data"):
        await update.message.reply_text(f"Không thể tìm thấy thông tin cho mã `{tracking_code}`\. Vui lòng kiểm tra lại\.", parse_mode=ParseMode.MARKDOWN_V2)
        return

    records = data["data"]["sls_tracking_info"]["records"]
    last_update_time = records[0]['actual_time'] if records else 0
    last_status_description = records[0]['description'] if records else ""

    if db.add_tracked_order(conn, chat_id, tracking_code, last_update_time, last_status_description):
        await update.message.reply_text(f"✅ Đã bắt đầu theo dõi mã vận đơn: `{tracking_code}`", parse_mode=ParseMode.MARKDOWN_V2)
        if records:
            await update.message.reply_text(spx_service.format_status_message(tracking_code, records[0]), parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text("Đã có lỗi xảy ra khi lưu vào database\.", parse_mode=ParseMode.MARKDOWN_V2)

async def untrack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    if not context.args:
        await update.message.reply_text("Vui lòng nhập mã vận đơn\. \nVí dụ: `/untrack SPXVN0123456789`", parse_mode=ParseMode.MARKDOWN_V2)
        return
        
    tracking_code = context.args[0].upper()
    conn = context.bot_data['db_connection']

    if not db.get_tracked_order(conn, chat_id, tracking_code):
        await update.message.reply_text(f"Bạn không theo dõi mã `{tracking_code}`\.", parse_mode=ParseMode.MARKDOWN_V2)
        return

    if db.remove_tracked_order(conn, chat_id, tracking_code):
        await update.message.reply_text(f"🗑️ Đã ngừng theo dõi mã vận đơn: `{tracking_code}`", parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text("Đã có lỗi xảy ra khi xóa khỏi database\.", parse_mode=ParseMode.MARKDOWN_V2)

async def list_tracked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conn = context.bot_data['db_connection']
    codes = db.get_user_tracked_orders(conn, update.message.chat_id)

    if not codes:
        await update.message.reply_text("Bạn chưa theo dõi mã vận đơn nào cả\.")
    else:
        message = "📋 *Danh sách các mã vận đơn đang theo dõi:*\n"
        for code_row in codes:
            message += f"\\- `{spx_service.escape_md(code_row['tracking_code'])}`\n"
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)

async def status_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Vui lòng nhập mã vận đơn\. \nVí dụ: `/status SPXVN0123456789`", parse_mode=ParseMode.MARKDOWN_V2)
        return
    
    tracking_code = context.args[0].upper()
    data = spx_service.fetch_spx_data(tracking_code)

    if not data or data.get("retcode") != 0 or not data.get("data"):
        await update.message.reply_text(f"Không tìm thấy thông tin cho mã `{tracking_code}`\.", parse_mode=ParseMode.MARKDOWN_V2)
        return
    
    records = data["data"]["sls_tracking_info"]["records"]
    if not records:
        await update.message.reply_text(f"Mã `{tracking_code}` chưa có lịch sử vận chuyển\.", parse_mode=ParseMode.MARKDOWN_V2)
        return

    message = spx_service.format_status_message(tracking_code, records[0])
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Vui lòng nhập mã vận đơn\. \nVí dụ: `/history SPXVN0123456789`", parse_mode=ParseMode.MARKDOWN_V2)
        return
    
    tracking_code = context.args[0].upper()
    data = spx_service.fetch_spx_data(tracking_code)

    if not data or data.get("retcode") != 0 or not data.get("data"):
        await update.message.reply_text(f"Không tìm thấy thông tin cho mã `{tracking_code}`\.", parse_mode=ParseMode.MARKDOWN_V2)
        return
    
    records = data["data"]["sls_tracking_info"]["records"]
    if not records:
        await update.message.reply_text(f"Mã `{tracking_code}` chưa có lịch sử vận chuyển\.", parse_mode=ParseMode.MARKDOWN_V2)
        return

    message = spx_service.format_history_message(tracking_code, records)
    
    if len(message) > 4096:
        for i in range(0, len(message), 4096):
            await update.message.reply_text(message[i:i+4096], parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)

async def check_for_updates(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Công việc chạy nền để kiểm tra tất cả các đơn hàng một cách an toàn."""
    conn = db.get_db_connection()
    if not conn:
        logger.error("check_for_updates: Không thể tạo kết nối DB.")
        return

    try:
        all_orders = db.get_all_tracked_orders(conn)
        logger.info(f"Đang chạy tác vụ kiểm tra định kỳ cho {len(all_orders)} đơn hàng.")

        for order in all_orders:
            # === SỬA LỖI: Bọc logic xử lý mỗi đơn hàng trong try...except ===
            # Điều này đảm bảo lỗi của một đơn hàng không làm sập toàn bộ tác vụ.
            try:
                chat_id = order['chat_id']
                tracking_code = order['tracking_code']
                last_update_time = order['last_update_time']
                last_status_description = order['last_status_description']

                data = spx_service.fetch_spx_data(tracking_code)
                if not data or data.get("retcode") != 0 or not data.get("data"):
                    continue # Bỏ qua nếu API lỗi hoặc không có dữ liệu
                
                records = data["data"]["sls_tracking_info"]["records"]
                if not records:
                    continue

                latest_record = records[0]
                new_update_time = latest_record.get('actual_time', 0)
                new_description = latest_record.get('description', "")

                # Chỉ thông báo nếu thời gian mới hơn HOẶC mô tả khác đi
                if new_update_time > last_update_time or new_description != last_status_description:
                    logger.info(f"Phát hiện cập nhật cho mã {tracking_code} của chat_id {chat_id}")
                    message = spx_service.format_status_message(tracking_code, latest_record)
                    
                    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN_V2)
                    
                    # Cập nhật cả thời gian và mô tả mới vào DB
                    db.update_order_status(conn, chat_id, tracking_code, new_update_time, new_description)

                    # Tự động untrack khi giao hàng thành công
                    if latest_record.get("milestone_code") == 8: # 8 = "Delivered"
                        await context.bot.send_message(chat_id=chat_id, text=f"🎉 Đơn hàng `{spx_service.escape_md(tracking_code)}` đã giao thành công và được tự động xóa khỏi danh sách theo dõi\.", parse_mode=ParseMode.MARKDOWN_V2)
                        db.remove_tracked_order(conn, chat_id, tracking_code)

            except Exception as e:
                # Ghi lại lỗi của một đơn hàng cụ thể và tiếp tục vòng lặp
                logger.error(f"Lỗi khi xử lý đơn hàng {order.get('tracking_code', 'N/A')}: {e}")
                continue
    
    finally:
        if conn:
            conn.close()
            logger.info("Tác vụ kiểm tra định kỳ đã hoàn thành và đóng kết nối DB.")