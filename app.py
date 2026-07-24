import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# Initialize ORM instance
db = SQLAlchemy()

# Define the Database Model (ORM replacement for raw SQL tables)
class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Expense {self.item} - ${self.amount}>"

def create_app():
    app = Flask(__name__)
    
    # Application Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-local-only')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()  # Automatically creates database tables based on models

    @app.route('/')
    def home():
        # 1. Fetch all expenses ordered by newest first
        expenses = Expense.query.order_by(Expense.id.desc()).all()
        
        # 2. Calculate the total sum of all expenses
        total = sum(e.amount for e in expenses)
        
        # 3. Pass BOTH expenses and total into index.html
        return render_template('index.html', expenses=expenses, total=total)

    @app.route('/add', methods=['POST'])
    def add_expense():
        item = request.form.get('item', '').strip()
        amount_raw = request.form.get('amount', '').strip()

        # Server-Side Input Validation
        if not item or not amount_raw:
            flash("All fields are required.", "error")
            return redirect(url_for('home'))

        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Please enter a valid positive amount.", "error")
            return redirect(url_for('home'))

        # Add new entry via SQLAlchemy ORM
        new_expense = Expense(item=item, amount=amount)
        db.session.add(new_expense)
        db.session.commit()

        return redirect(url_for('home'))

    @app.route('/delete/<int:id>', methods=['POST'])
    def delete_expense(id):
        # Delete entry via SQLAlchemy ORM
        expense = Expense.query.get_or_404(id)
        db.session.delete(expense)
        db.session.commit()
        
        return redirect(url_for('home'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)