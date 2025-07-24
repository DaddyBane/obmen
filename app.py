from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os

app = Flask("app")
CORS(app)

DB = 'database.db'

def get_db():
    conn = sqlite3.connect(DB)
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
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.json
    print("Получена заявка:", data)
    try:
        with get_db() as db:
            db.execute(
                '''INSERT INTO requests 
                (name, contact, from_currency, to_currency, amount, crypto_address, time, status, payment_info) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (data['name'], data['contact'], data['from_currency'], data['to_currency'],
                 data['amount'], data['crypto_address'], datetime.now().isoformat(), 'new', '')
            )
        return jsonify({'ok': True})
    except Exception as e:
        print("Ошибка при сохранении:", e)
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/requests')
def get_requests():
    try:
        with get_db() as db:
            cursor = db.execute('SELECT * FROM requests ORDER BY id DESC')
            rows = cursor.fetchall()
            requests_list = [dict(row) for row in rows]
        return jsonify(requests_list)
    except Exception as e:
        print("Ошибка при получении заявок:", e)
        return jsonify([]), 500

@app.route('/api/update', methods=['POST'])
def update_request():
    data = request.json
    try:
        with get_db() as db:
            db.execute(
                'UPDATE requests SET status = ?, payment_info = ? WHERE id = ?',
                (data.get('status', ''), data.get('payment_info', ''), data['id'])
            )
        return jsonify({'ok': True})
    except Exception as e:
        print("Ошибка при обновлении заявки:", e)
        return jsonify({'ok': False, 'error': str(e)}), 500

if True:
    init_db()
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
