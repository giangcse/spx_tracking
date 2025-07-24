# database.py

import sqlite3
import config

def get_db_connection():
    """Tạo và trả về một kết nối đến database."""
    try:
        conn = sqlite3.connect(config.DB_NAME, check_same_thread=False)
        # Giúp truy cập các cột bằng tên, ví dụ: row['chat_id']
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Lỗi kết nối database: {e}")
        return None

def setup_database(conn):
    """Tạo bảng tracked_orders nếu nó chưa tồn tại."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracked_orders (
                chat_id INTEGER NOT NULL,
                tracking_code TEXT NOT NULL,
                last_update_time INTEGER DEFAULT 0,
                PRIMARY KEY (chat_id, tracking_code)
            )
        ''')
        conn.commit()
        print("Database đã được thiết lập thành công.")
    except sqlite3.Error as e:
        print(f"Lỗi thiết lập database: {e}")

def add_tracked_order(conn, chat_id, tracking_code, last_update_time):
    """Thêm một mã vận đơn vào danh sách theo dõi."""
    sql = "INSERT INTO tracked_orders (chat_id, tracking_code, last_update_time) VALUES (?, ?, ?)"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (chat_id, tracking_code, last_update_time))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Lỗi thêm đơn hàng: {e}")
        return False

def get_tracked_order(conn, chat_id, tracking_code):
    """Kiểm tra xem một đơn hàng đã được theo dõi bởi người dùng chưa."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracked_orders WHERE chat_id = ? AND tracking_code = ?", (chat_id, tracking_code))
    return cursor.fetchone()

def remove_tracked_order(conn, chat_id, tracking_code):
    """Xóa một mã vận đơn khỏi danh sách theo dõi."""
    sql = "DELETE FROM tracked_orders WHERE chat_id = ? AND tracking_code = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (chat_id, tracking_code))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Lỗi xóa đơn hàng: {e}")
        return False

def get_user_tracked_orders(conn, chat_id):
    """Lấy tất cả các mã vận đơn mà một người dùng đang theo dõi."""
    cursor = conn.cursor()
    cursor.execute("SELECT tracking_code FROM tracked_orders WHERE chat_id = ?", (chat_id,))
    return cursor.fetchall()

def get_all_tracked_orders(conn):
    """Lấy tất cả các đơn hàng từ tất cả người dùng để kiểm tra cập nhật."""
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, tracking_code, last_update_time FROM tracked_orders")
    return cursor.fetchall()

def update_order_time(conn, chat_id, tracking_code, new_update_time):
    """Cập nhật thời gian trạng thái mới nhất cho một đơn hàng."""
    sql = "UPDATE tracked_orders SET last_update_time = ? WHERE chat_id = ? AND tracking_code = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (new_update_time, chat_id, tracking_code))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Lỗi cập nhật thời gian đơn hàng: {e}")
        return False