import os

class Config:
    SECRET_KEY = 'expense-tracker-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///expenses.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False