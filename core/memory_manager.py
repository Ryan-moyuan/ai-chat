"""记忆管理 - SQLite 存储对话历史"""
import sqlite3
import os
import uuid
from datetime import datetime
from config_loader import DATA_DIR


DB_PATH = os.path.join(DATA_DIR, "conversations.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER,
            type TEXT,
            comment TEXT,
            timestamp TEXT,
            FOREIGN KEY (message_id) REFERENCES messages(id)
        )
    """)
    conn.commit()
    conn.close()


def create_conversation(title="新对话"):
    """创建新会话"""
    conn = _get_conn()
    conv_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    conn.execute("INSERT INTO conversations VALUES (?, ?, ?)", (conv_id, title, now))
    conn.commit()
    conn.close()
    return conv_id


def save_message(conv_id, role, content):
    """保存消息"""
    conn = _get_conn()
    now = datetime.now().isoformat()
    cursor = conn.execute(
        "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (conv_id, role, content, now),
    )
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()
    return msg_id


def get_conversation_messages(conv_id, limit=None):
    """获取会话消息"""
    conn = _get_conn()
    query = "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC"
    if limit:
        query += f" LIMIT {int(limit)}"
    rows = conn.execute(query, (conv_id,)).fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in rows]


def get_conversations():
    """获取所有会话列表"""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT id, title, created_at FROM conversations ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [{"id": r["id"], "title": r["title"], "created_at": r["created_at"]} for r in rows]


def get_conversation_title(conv_id):
    conn = _get_conn()
    row = conn.execute("SELECT title FROM conversations WHERE id = ?", (conv_id,)).fetchone()
    conn.close()
    return row["title"] if row else "未命名"


def update_conversation_title(conv_id, title):
    conn = _get_conn()
    conn.execute("UPDATE conversations SET title = ? WHERE id = ?", (title, conv_id))
    conn.commit()
    conn.close()


def delete_conversation(conv_id):
    conn = _get_conn()
    conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
    conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
    conn.commit()
    conn.close()


def save_feedback(msg_id, feedback_type, comment=""):
    """保存反馈 (thumbs up/down)"""
    conn = _get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO feedback (message_id, type, comment, timestamp) VALUES (?, ?, ?, ?)",
        (msg_id, feedback_type, comment, now),
    )
    conn.commit()
    conn.close()


def get_feedback_stats():
    """获取反馈统计"""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT type, COUNT(*) as count FROM feedback GROUP BY type"
    ).fetchall()
    conn.close()
    return {r["type"]: r["count"] for r in rows}
