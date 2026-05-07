from flask_login import UserMixin
from datetime import datetime

def init_models(db):
    class User(UserMixin, db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password = db.Column(db.String(200), nullable=False)
        telegram_id = db.Column(db.String(50), unique=True, nullable=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        expenses = db.relationship('Expense', backref='user', lazy=True)

    class Expense(db.Model):
        __tablename__ = 'expenses'
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=False)
        amount = db.Column(db.Float, nullable=False)
        category = db.Column(db.String(50), nullable=False)
        date = db.Column(db.DateTime, default=datetime.utcnow)
        description = db.Column(db.String(200))
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    return User, Expense