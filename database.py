# database.py

import sqlite3
import config

def get_db_connection():
    """Tạo và trả về một kết nối đến database."""
    try:
        conn = sqlite3.connect(config.DB_NAME, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Lỗi kết nối database: {e}")
        return None

def setup_database(conn):
    """Tạo hoặc cập nhật bảng tracked_orders nếu cần."""
    try:
        cursor = conn.cursor()
        # Sửa đổi bảng để thêm cột last_status_description
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracked_orders (
                chat_id INTEGER NOT NULL,
                tracking_code TEXT NOT NULL,
                last_update_time INTEGER DEFAULT 0,
                last_status_description TEXT, 
                PRIMARY KEY (chat_id, tracking_code)
            )
        ''')
        
        # Thêm cột mới nếu chưa có (để tương thích với database cũ)
        cursor.execute("PRAGMA table_info(tracked_orders)")
        columns = [column['name'] for column in cursor.fetchall()]
        if 'last_status_description' not in columns:
            cursor.execute("ALTER TABLE tracked_orders ADD COLUMN last_status_description TEXT")

        conn.commit()
        print("Database đã được thiết lập thành công.")
    except sqlite3.Error as e:
        print(f"Lỗi thiết lập database: {e}")

def add_tracked_order(conn, chat_id, tracking_code, last_update_time, last_status_description):
    """Thêm một mã vận đơn vào danh sách theo dõi."""
    sql = "INSERT INTO tracked_orders (chat_id, tracking_code, last_update_time, last_status_description) VALUES (?, ?, ?, ?)"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (chat_id, tracking_code, last_update_time, last_status_description))
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
    cursor.execute("SELECT chat_id, tracking_code, last_update_time, last_status_description FROM tracked_orders")
    return cursor.fetchall()

def update_order_status(conn, chat_id, tracking_code, new_time, new_description):
    """Cập nhật trạng thái mới nhất cho một đơn hàng."""
    sql = "UPDATE tracked_orders SET last_update_time = ?, last_status_description = ? WHERE chat_id = ? AND tracking_code = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (new_time, new_description, chat_id, tracking_code))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Lỗi cập nhật trạng thái đơn hàng: {e}")
        return False