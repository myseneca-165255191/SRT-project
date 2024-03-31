import sqlite3
import time
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Set up SQLite database connection
conn = sqlite3.connect('transactions.db', check_same_thread=False)
cursor = conn.cursor()

# Create transaction log table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        sender TEXT NOT NULL,
        recipient TEXT NOT NULL,
        amount INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Initialize balance
balance = 1000


@app.route('/', methods=['GET', 'POST'])
def index():
    global balance
    error_message = ""
    success_message = ""

    if request.method == 'POST':
        sender = request.form['sender']
        recipient = request.form['recipient']
        amount = int(request.form['amount'])

        if amount > balance:
            error_message = 'Insufficient balance. Please try again.'
        else:
            # Log the transaction to the database
            cursor.execute('''
                INSERT INTO transactions (sender, recipient, amount) VALUES (?, ?, ?)
            ''', (sender, recipient, amount))
            conn.commit()

            balance -= amount
            success_message = f"Money sent from {sender} to {recipient} for {amount}!"
            time.sleep(1)
            return redirect(url_for('receipt', sender=sender, recipient=recipient, amount=amount))

    return render_template('index.html', balance=balance, error=error_message, success=success_message)


@app.route('/receipt')
def receipt():
    sender = request.args.get('sender')
    recipient = request.args.get('recipient')
    amount = request.args.get('amount')

    # Retrieve transaction logs from the database
    cursor.execute('''
        SELECT * FROM transactions WHERE sender = ? AND recipient = ? AND amount = ?
    ''', (sender, recipient, amount))
    transaction_logs = cursor.fetchall()

    return render_template('receipt.html', sender=sender, recipient=recipient, amount=amount,
                           transaction_logs=transaction_logs)


if __name__ == '__main__':
    app.run(debug=True)
