# spx_service.py

import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def fetch_spx_data(tracking_code: str):
    """Lấy dữ liệu vận đơn từ API của SPX."""
    api_url = f"https://spx.vn/shipment/order/open/order/get_order_info?spx_tn={tracking_code}&language_code=vi"
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()  # Báo lỗi nếu request không thành công
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi gọi API SPX cho mã {tracking_code}: {e}")
        return None

def escape_md(text: str) -> str:
    """Hàm để escape các ký tự đặc biệt cho MarkdownV2."""
    escape_chars = r'._*[]()~`>#+-=|{}!'
    return "".join([f'\\{char}' if char in escape_chars else char for char in str(text)])

def format_status_message(tracking_code: str, record: dict) -> str:
    """Định dạng trạng thái mới nhất thành tin nhắn dễ đọc."""
    status_description = record.get("description", "Không có mô tả")
    timestamp = record.get("actual_time")
    status_time = datetime.fromtimestamp(timestamp).strftime('%H:%M ngày %d-%m-%Y') if timestamp else "N/A"
    location = record.get("current_location", {}).get("location_name", "")

    message = f"📦 *Cập nhật cho đơn* `{escape_md(tracking_code)}`\n\n"
    message += f"🕒 *Thời gian:* {escape_md(status_time)}\n"
    message += f"📝 *Trạng thái:* {escape_md(status_description)}\n"
    if location:
        message += f"📍 *Vị trí:* {escape_md(location)}"
    return message

def format_history_message(tracking_code: str, records: list) -> str:
    """Định dạng toàn bộ lịch sử vận đơn thành một tin nhắn."""
    message = f"📜 *Toàn bộ lịch sử đơn hàng* `{escape_md(tracking_code)}`\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n\n"

    # API trả về từ mới nhất -> cũ nhất, nên ta cần đảo ngược lại để hiển thị
    for record in reversed(records):
        status_description = record.get("description", "N/A")
        timestamp = record.get("actual_time")
        status_time = datetime.fromtimestamp(timestamp).strftime('%H:%M %d-%m-%Y') if timestamp else "N/A"
        
        message += f"🕒 `{escape_md(status_time)}`\n"
        message += f"\\- {escape_md(status_description)}\n\n"
    
    return message