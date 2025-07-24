from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)

DB_PATH = "database.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                contact TEXT,
                from_currency TEXT,
                to_currency TEXT,
                amount REAL,
                crypto_address TEXT,
                time TEXT,
                status TEXT,
                payment_info TEXT
            )
        ''')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/api/submit', methods=["POST"])
def submit():
    data = request.json
    with get_db() as db:
        db.execute("""
            INSERT INTO requests 
            (name, contact, from_currency, to_currency, amount, crypto_address, time, status, payment_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data['name'], 
                data['contact'], 
                data['from_currency'], 
                data['to_currency'], 
                data['amount'], 
                data['crypto_address'], 
                datetime.now().isoformat(), 
                "new", 
                ""
            )
        )
    return jsonify({"ok": True})

@app.route('/api/requests')
def get_requests():
    with get_db() as db:
        cur = db.execute("SELECT * FROM requests ORDER BY time DESC")
        rows = cur.fetchall()
        data = [dict(row) for row in rows]
    return jsonify(data)

@app.route('/api/update', methods=["POST"])
def update():
    data = request.json
    with get_db() as db:
        db.execute("""
            UPDATE requests SET status = ?, payment_info = ? WHERE id = ?
        """, (data['status'], data.get('payment_info', ''), data['id']))
    return jsonify({"ok": True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
