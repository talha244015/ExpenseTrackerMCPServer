from fastmcp import FastMCP
from datetime import date

mcp=FastMCP("DemoServer")
import sqlite3

def get_conn():
    conn = sqlite3.connect("ExpenseTracker.db")
    conn.row_factory = sqlite3.Row
    return conn
def create_user_table():
    conn = get_conn()
    try:
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users
                   (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL
                    )''')
    finally:
        conn.close()
def create_expensetable():
    conn = get_conn()
    try:
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS expenses
                   (expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    detail TEXT,
                    date TEXT NOT NULL)''')
    finally:
        conn.close()
@mcp.tool 
def insert_expense( category, price, my_date:date, detail, user_id:int):
    
    """my_date must be in format YYYY-MM-DD"""
    conn = get_conn()
    try:
        with conn:
           conn.execute("INSERT INTO expenses (category, price, date, detail) VALUES (?, ?, ?, ?)", (category, price, my_date.isoformat(), detail))
    finally:
        conn.close()
@mcp.tool
def update_expense(user_id:int, expense_id:int, category, price, date, detail):
    conn = get_conn()
    try:
        with conn:
            conn.execute("UPDATE expenses SET category = ?, price = ?, date = ?, detail = ? WHERE expense_id = ? AND user_id = ?", (category, price, date, detail, expense_id, user_id))
    finally:
        conn.close()
@mcp.tool
def delete_expense(user_id:int, expense_id:int):
    conn = get_conn()
    try:
        with conn:
            conn.execute("DELETE FROM expenses WHERE expense_id = ? AND user_id = ?", (expense_id, user_id))
    finally:
        conn.close()
@mcp.tool
def get_expenses_between(start_date:date, end_date:date):
    conn = get_conn()
    try:
        with conn:
            curr=conn.execute("SELECT * FROM expenses WHERE date BETWEEN ? AND ?", (start_date.isoformat(), end_date.isoformat()))
            return [dict(row) for row in curr]
    finally:
        conn.close()
@mcp.tool
def get_all_expenses():
    conn = get_conn()
    try:
        with conn:
            curr=conn.execute("SELECT * FROM expenses")
            return [dict(row) for row in curr]
    finally:
        conn.close()
create_user_table()
create_expensetable()
def main():
    mcp.run()
    