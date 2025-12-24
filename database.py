import sqlite3
from datetime import datetime

DB_NAME = "finance.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_transaction(type_, category, amount, description, date):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (type, category, amount, description, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (type_, category, float(amount), description, date))
    conn.commit()
    conn.close()

def get_transactions():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM transactions ORDER BY date DESC, id DESC')
    rows = c.fetchall()
    conn.close()
    # Convert Row objects to dicts for easier handling
    return [dict(row) for row in rows]

def get_transaction_by_id(id_):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM transactions WHERE id = ?', (id_,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_transaction(id_, type_, category, amount, description, date):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE transactions 
        SET type = ?, category = ?, amount = ?, description = ?, date = ?
        WHERE id = ?
    ''', (type_, category, float(amount), description, date, id_))
    conn.commit()
    conn.close()

def delete_transaction(id_):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM transactions WHERE id = ?', (id_,))
    conn.commit()
    conn.close()

def get_summary():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Income'")
    total_income = c.fetchone()[0] or 0.0
    
    c.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Outcome'")
    total_outcome = c.fetchone()[0] or 0.0
    
    conn.close()
    return {
        "total_income": total_income,
        "total_outcome": total_outcome,
        "balance": total_income - total_outcome
    }