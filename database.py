import sqlite3
import logging

logger = logging.getLogger(__name__)
DB_NAME = "expenses.db"

def init_db():
    """Инициализация базы данных и создание таблицы расходов."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            category TEXT NOT NULL,
            expense_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Создаем индекс для быстрого поиска по пользователю и дате
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_date ON expenses(user_id, expense_date)')
    conn.commit()
    conn.close()
    logger.info("База данных успешно инициализирована.")

def add_expense(user_id: int, amount: float, category: str, date: str) -> bool:
    """Добавление новой записи о расходе в базу данных."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (user_id, amount, category, expense_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, amount, category, date))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"Ошибка при добавлении расхода: {e}")
        return False

def get_monthly_stats(user_id: int) -> list:
    """Получение статистики расходов пользователя за текущий месяц по категориям."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Группируем суммы по категориям для текущего пользователя
    cursor.execute('''
        SELECT category, SUM(amount) 
        FROM expenses 
        WHERE user_id = ? 
        GROUP BY category
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows