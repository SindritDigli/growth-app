import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE phase ADD COLUMN status TEXT DEFAULT 'In corso'")
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        progress INTEGER DEFAULT 0,
        status TEXT DEFAULT 'In corso',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phase (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        start_date TEXT DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'In corso'
    )
""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT DEFAULT CURRENT_DATE,
    value INTEGER NOT NULL  -- -1 peggioramento, 0 mantenimento, +1 miglioramento
)
""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS progress_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    data TEXT NOT NULL
)
""")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database creato.")