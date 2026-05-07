from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    from app import db
    from models import User
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('main.register'))

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    from models import User
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('main.login'))

        login_user(user)
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    from models import Expense
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    total = sum(e.amount for e in expenses)
    category_data = {}
    for e in expenses:
        category_data[e.category] = category_data.get(e.category, 0) + e.amount
    return render_template('dashboard.html', expenses=expenses, total=total, category_data=category_data)

@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    from app import db
    from models import Expense
    if request.method == 'POST':
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
        new_expense = Expense(
            title=request.form.get('title'),
            amount=float(request.form.get('amount')),
            category=request.form.get('category'),
            description=request.form.get('description'),
            date=date,
            user_id=current_user.id
        )
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('expenses.html')

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    from app import db
    from models import Expense
    expense = Expense.query.get_or_404(id)
    if expense.user_id != current_user.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        expense.title = request.form.get('title')
        expense.amount = float(request.form.get('amount'))
        expense.category = request.form.get('category')
        expense.description = request.form.get('description')
        date_str = request.form.get('date')
        if date_str:
            expense.date = datetime.strptime(date_str, '%Y-%m-%d')
        db.session.commit()
        flash('Expense updated!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('expenses.html', expense=expense)

@main.route('/delete/<int:id>')
@login_required
def delete_expense(id):
    from app import db
    from models import Expense
    expense = Expense.query.get_or_404(id)
    if expense.user_id != current_user.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('main.dashboard'))
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted!', 'success')
    return redirect(url_for('main.dashboard'))