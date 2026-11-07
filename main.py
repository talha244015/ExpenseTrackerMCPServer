
from datetime import date
import os
from fastmcp import FastMCP
from fastmcp.server.auth.providers.auth0 import Auth0Provider
from fastmcp.server.dependencies import get_access_token

auth = Auth0Provider(
    config_url=f"https://{os.environ['AUTH0_DOMAIN']}/.well-known/openid-configuration",
    client_id=os.environ["AUTH0_CLIENT_ID"],
    client_secret=os.environ["AUTH0_CLIENT_SECRET"],
    audience=os.environ["AUTH0_AUDIENCE"],
    base_url=os.environ.get("BASE_URL", "http://localhost:8000"),
)

mcp = FastMCP("DemoServer", auth=auth)



def current_user() -> str:
    token = get_access_token()
    sub = token.claims.get("sub")
    if not sub:
        raise PermissionError("No user identity in token")
    return sub
import sqlite3
def get_conn():
    conn = sqlite3.connect(os.environ.get("DB_PATH", "ExpenseTracker.db"))
    conn.row_factory = sqlite3.Row
    return conn


def create_expensetable():
    conn = get_conn()
    try:
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS expenses
                   (expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    detail TEXT,
                    date TEXT NOT NULL)''')
    finally:
        conn.close()
@mcp.tool 
def insert_expense( category:str, price:float, my_date:date, detail:str):
    """my_date must be in format YYYY-MM-DD"""
    conn = get_conn()
    try:
        with conn:
           conn.execute("INSERT INTO expenses (category, price, date, detail, user_id) VALUES (?, ?, ?, ?, ?)", (category, price, my_date.isoformat(), detail, current_user()))
    finally:
        conn.close()
@mcp.tool
def update_expense( expense_id:int, category:str, price:float,my_date: date, detail:str):
    conn = get_conn()
    try:
        with conn:
            conn.execute("UPDATE expenses SET category = ?, price = ?, date = ?, detail = ? WHERE expense_id = ? AND user_id = ?", (category, price, my_date.isoformat(), detail, expense_id, current_user()))
    finally:
        conn.close()
@mcp.tool
def delete_expense(expense_id:int):
    conn = get_conn()
    try:
        with conn:
            conn.execute("DELETE FROM expenses WHERE expense_id = ? AND user_id = ?", (expense_id, current_user()))
    finally:
        conn.close()
@mcp.tool
def get_expenses_between(start_date:date, end_date:date):
    conn = get_conn()
    try:
        with conn:
            curr=conn.execute("SELECT * FROM expenses WHERE user_id = ? AND date BETWEEN ? AND ?", (current_user(), start_date.isoformat(), end_date.isoformat()))
            return [dict(row) for row in curr]
    finally:
        conn.close()
@mcp.tool
def get_all_expenses():
    conn = get_conn()
    try:
        with conn:
            curr=conn.execute("SELECT * FROM expenses WHERE user_id = ?", (current_user(),))
            return [dict(row) for row in curr]
    finally:
        conn.close()

create_expensetable()

def main():
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

if __name__ == "__main__":
    main()