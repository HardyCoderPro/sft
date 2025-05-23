import sqlite3
from datetime import datetime
import os

DB_FILE = 'users.db'

def init_db():
    """Veritabanı tablolarını oluşturur veya varsa bağlantı kurar"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Kullanıcılar tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id TEXT UNIQUE,
                 username TEXT,
                 first_name TEXT,
                 last_name TEXT,
                 is_premium INTEGER DEFAULT 0,
                 premium_end DATE,
                 is_banned INTEGER DEFAULT 0,
                 ban_reason TEXT,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Aktivite tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS activity
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id TEXT,
                 api_endpoint TEXT,
                 parameters TEXT,
                 response TEXT,
                 timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Eski sürümler için tablo güncellemeleri
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]
    if 'first_name' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN first_name TEXT")
    if 'last_name' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN last_name TEXT")
    
    conn.commit()
    conn.close()

def get_user_activity(user_id, limit=10):
    """Kullanıcının sorgu geçmişini getirir"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT api_endpoint, parameters, response, timestamp 
        FROM activity 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (str(user_id), limit))
    activities = c.fetchall()
    conn.close()
    
    # Aktivite verilerini formatla
    formatted_activities = []
    for activity in activities:
        formatted_activities.append({
            'api': activity[0],
            'parameters': activity[1],
            'response': activity[2],
            'timestamp': activity[3]
        })
    
    return formatted_activities

def get_all_users():
    """Tüm kullanıcıları getirir"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT user_id, username, first_name, last_name, 
               is_premium, premium_end, is_banned, ban_reason
        FROM users
        ORDER BY created_at DESC
    """)
    users = c.fetchall()
    conn.close()
    return users

def add_user(user_id, username=None, first_name=None, last_name=None):
    """Yeni kullanıcı ekler veya günceller"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_name = excluded.last_name
        """, (str(user_id), username, first_name, last_name))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Kullanıcı ekleme hatası: {e}")
    finally:
        conn.close()

def get_user(user_id):
    """Tek bir kullanıcıyı getirir"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))
    user = c.fetchone()
    conn.close()
    return user

def check_premium(user_id):
    """Premium üyelik kontrolü"""
    user = get_user(user_id)
    if user and user[5] == 1:  # is_premium
        premium_end = user[6]  # premium_end
        if premium_end:
            try:
                if isinstance(premium_end, str):
                    premium_end = datetime.strptime(premium_end, "%Y-%m-%d")
                return premium_end > datetime.now()
            except (ValueError, TypeError):
                pass
    return False

def update_premium(user_id, is_premium, end_date):
    """Premium üyeliği günceller"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        UPDATE users 
        SET is_premium = ?, premium_end = ?
        WHERE user_id = ?
    """, (is_premium, end_date, str(user_id)))
    conn.commit()
    conn.close()

def ban_user(user_id, reason):
    """Kullanıcıyı yasaklar"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        UPDATE users 
        SET is_banned = 1, ban_reason = ?
        WHERE user_id = ?
    """, (reason, str(user_id)))
    conn.commit()
    conn.close()

def unban_user(user_id):
    """Kullanıcı yasağını kaldırır"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        UPDATE users 
        SET is_banned = 0, ban_reason = NULL
        WHERE user_id = ?
    """, (str(user_id),))
    conn.commit()
    conn.close()

def log_activity(user_id, api_endpoint, parameters, response):
    """Aktivite kaydı oluşturur"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO activity 
        (user_id, api_endpoint, parameters, response)
        VALUES (?, ?, ?, ?)
    """, (str(user_id), api_endpoint, str(parameters), str(response)))
    conn.commit()
    conn.close()

def check_rate_limit(user_id):
    """Sorgu limit kontrolü"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) FROM activity 
        WHERE user_id = ? 
        AND timestamp > datetime('now', '-1 minute')
    """, (str(user_id),))
    count = c.fetchone()[0]
    conn.close()
    return count < 5  # Dakikada 5 sorgu limiti

def get_user_stats(user_id):
    """Kullanıcının sorgu istatistiklerini getirir"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Toplam sorgu sayısı
    c.execute("SELECT COUNT(*) FROM activity WHERE user_id = ?", (str(user_id),))
    total_queries = c.fetchone()[0]
    
    # Bugünkü sorgu sayısı
    c.execute("""
        SELECT COUNT(*) FROM activity 
        WHERE user_id = ? 
        AND DATE(timestamp) = DATE('now')
    """, (str(user_id),))
    today_queries = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total': total_queries,
        'today': today_queries
    }

if __name__ == "__main__":
    init_db()
    print("Veritabanı başlatıldı. Tüm tablolar hazır.")