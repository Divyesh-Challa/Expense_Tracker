import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  
    return conn

@app.route('/')
def home():
    
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses').fetchall()
    conn.close()
    
    
    return render_template('index.html', expenses=expenses)

@app.route('/add', methods=['POST'])
def add_expense():
    
    item_name = request.form['item']
    item_amount = request.form['amount']
    
    
    conn = get_db_connection()
    conn.execute('INSERT INTO expenses (item, amount) VALUES (?, ?)',
                 (item_name, item_amount))
    conn.commit()
    conn.close()
    
   
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)