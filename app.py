import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ==========================================
# DATABASE MODELS
# ==========================================

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(50), nullable=False, default='General')
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Budget(db.Model):
    __tablename__ = 'budgets'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), unique=True, nullable=False)
    monthly_limit = db.Column(db.Float, nullable=False)

class Investment(db.Model):
    __tablename__ = 'investments'
    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(100), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    shares = db.Column(db.Float, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)

# ==========================================
# APPLICATION FACTORY
# ==========================================

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'financial-dashboard-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def dashboard():
        transactions = Transaction.query.order_by(Transaction.date.desc()).all()
        budgets = Budget.query.all()
        investments = Investment.query.all()

        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
        net_cash_flow = total_income - total_expenses

        portfolio_value = sum(i.shares * i.current_price for i in investments)
        portfolio_cost = sum(i.shares * i.buy_price for i in investments)
        portfolio_gain = portfolio_value - portfolio_cost

        budget_progress = []
        for b in budgets:
            spent = sum(t.amount for t in transactions if t.category == b.category and t.type == 'expense')
            pct = min(100, int((spent / b.monthly_limit) * 100)) if b.monthly_limit > 0 else 0
            budget_progress.append({
                'category': b.category,
                'limit': b.monthly_limit,
                'spent': spent,
                'percentage': pct
            })

        return render_template(
            'index.html',
            transactions=transactions,
            total_income=total_income,
            total_expenses=total_expenses,
            net_cash_flow=net_cash_flow,
            portfolio_value=portfolio_value,
            portfolio_gain=portfolio_gain,
            budget_progress=budget_progress,
            investments=investments
        )

    @app.route('/transaction/add', methods=['POST'])
    def add_transaction():
        title = request.form.get('title', '').strip()
        amount_raw = request.form.get('amount', '').strip()
        trans_type = request.form.get('type', 'expense')
        category = request.form.get('category', 'General').strip()

        if title and amount_raw:
            try:
                amount = float(amount_raw)
                if amount > 0:
                    new_t = Transaction(title=title, amount=amount, type=trans_type, category=category)
                    db.session.add(new_t)
                    db.session.commit()
            except ValueError:
                flash("Invalid transaction amount.", "error")

        return redirect(url_for('dashboard'))

    @app.route('/transaction/delete/<int:id>', methods=['POST'])
    def delete_transaction(id):
        t = Transaction.query.get_or_404(id)
        db.session.delete(t)
        db.session.commit()
        return redirect(url_for('dashboard'))

    @app.route('/budget/set', methods=['POST'])
    def set_budget():
        category = request.form.get('category', '').strip()
        limit_raw = request.form.get('limit', '').strip()

        if category and limit_raw:
            try:
                limit = float(limit_raw)
                existing = Budget.query.filter_by(category=category).first()
                if existing:
                    existing.monthly_limit = limit
                else:
                    db.session.add(Budget(category=category, monthly_limit=limit))
                db.session.commit()
            except ValueError:
                flash("Invalid budget target.", "error")

        return redirect(url_for('dashboard'))

    @app.route('/investment/add', methods=['POST'])
    def add_investment():
        asset_name = request.form.get('asset_name', '').strip()
        ticker = request.form.get('ticker', '').strip().upper()
        shares = float(request.form.get('shares', 0))
        buy_price = float(request.form.get('buy_price', 0))
        current_price = float(request.form.get('current_price', buy_price))

        if asset_name and ticker and shares > 0:
            inv = Investment(
                asset_name=asset_name,
                ticker=ticker,
                shares=shares,
                buy_price=buy_price,
                current_price=current_price
            )
            db.session.add(inv)
            db.session.commit()

        return redirect(url_for('dashboard'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)