from flask import Flask, render_template, redirect, request, url_for
import sqlite3
import random

app = Flask(__name__)

DATABASE = 'game.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    telegram_id = request.args.get('id')
    referrer_id = request.args.get('ref')
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute('INSERT INTO users (telegram_id, referrer_id) VALUES (?, ?)', (telegram_id, referrer_id))
        db.commit()
        if referrer_id:
            bonus = 0.01
            cursor.execute('UPDATE users SET referral_bonus = referral_bonus + ?, balance = balance + ? WHERE telegram_id = ?', (bonus, bonus, referrer_id))
            db.commit()
        user = cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()

    return render_template('index.html', balance=user['balance'], upgrade_level=user['upgrade_level'], telegram_id=telegram_id)

@app.route('/click')
def click():
    telegram_id = request.args.get('id')
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT upgrade_level FROM users WHERE telegram_id = ?', (telegram_id,))
    user = cursor.fetchone()

    amount = random.uniform(0.001, 0.005) * (1 + user['upgrade_level'])
    cursor.execute('UPDATE users SET balance = balance + ? WHERE telegram_id = ?', (amount, telegram_id))
    db.commit()

    return redirect(url_for('index', id=telegram_id))

@app.route('/leaderboard')
def leaderboard():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT telegram_id, balance FROM users ORDER BY balance DESC LIMIT 10')
    top_players = cursor.fetchall()
    return render_template('leaderboard.html', players=top_players)

@app.route('/referrals')
def referrals():
    telegram_id = request.args.get('id')
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT referral_bonus FROM users WHERE telegram_id = ?', (telegram_id,))
    user = cursor.fetchone()
    referral_link = f"{request.url_root}?ref={telegram_id}"
    return render_template('referrals.html', bonus=user['referral_bonus'], referral_link=referral_link)

@app.route('/upgrade')
def upgrade():
    telegram_id = request.args.get('id')
    db = get_db()
    cursor = db.cursor()
    cost = 0.05
    cursor.execute('SELECT balance, upgrade_level FROM users WHERE telegram_id = ?', (telegram_id,))
    user = cursor.fetchone()
    
    if user['balance'] >= cost:
        new_balance = user['balance'] - cost
        new_level = user['upgrade_level'] + 1
        new_afk_income = user['afk_income'] + 0.001
        cursor.execute('UPDATE users SET balance = ?, upgrade_level = ?, afk_income = ? WHERE telegram_id = ?', (new_balance, new_level, new_afk_income, telegram_id))
        db.commit()
        
    return redirect(url_for('index', id=telegram_id))

if __name__ == '__main__':
    app.run(debug=True)
