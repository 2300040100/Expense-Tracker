import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
import re

import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

def get_category(title):
    title = title.lower()
    if any(w in title for w in ['lunch', 'dinner', 'breakfast', 'food', 'eat', 'swiggy', 'zomato']):
        return 'Food'
    elif any(w in title for w in ['bus', 'auto', 'uber', 'ola', 'train', 'transport', 'petrol']):
        return 'Transport'
    elif any(w in title for w in ['movie', 'game', 'netflix', 'entertainment']):
        return 'Entertainment'
    elif any(w in title for w in ['medicine', 'doctor', 'hospital', 'health']):
        return 'Healthcare'
    elif any(w in title for w in ['book', 'course', 'college', 'education', 'fees']):
        return 'Education'
    elif any(w in title for w in ['electricity', 'wifi', 'internet', 'bill']):
        return 'Utilities'
    elif any(w in title for w in ['shirt', 'shoes', 'clothes', 'shopping', 'amazon', 'flipkart']):
        return 'Shopping'
    else:
        return 'Other'

def parse_expense(text):
    pattern = r'spent\s+(\d+\.?\d*)\s+on\s+(.+)'
    match = re.match(pattern, text.strip().lower())
    if match:
        return float(match.group(1)), match.group(2).strip()
    return None, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to ExpenseTracker Bot!\n\n"
        "First link your account:\n"
        "/link your@email.com\n\n"
        "Then log expenses by sending:\n"
        "spent 150 on lunch\n"
        "spent 500 on uber\n\n"
        "/summary - View your expenses\n"
        "/help - Show this message"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 How to use:\n\n"
        "1️⃣ Link your account:\n"
        "/link your@email.com\n\n"
        "2️⃣ Log an expense:\n"
        "spent 150 on lunch\n"
        "spent 300 on uber\n\n"
        "3️⃣ Check summary:\n"
        "/summary"
    )

async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide your email!\nExample: /link your@email.com")
        return
    email = context.args[0]
    telegram_id = str(update.effective_user.id)

    from app import app, db, User
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            await update.message.reply_text("❌ No account found!\nPlease register on the website first.")
            return
        user.telegram_id = telegram_id
        db.session.commit()
        await update.message.reply_text(f"✅ Linked! Hello {user.username}!\nStart logging: spent 150 on lunch")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    from app import app, User, Expense
    with app.app_context():
        user = User.query.filter_by(telegram_id=telegram_id).first()
        if not user:
            await update.message.reply_text("❌ Please link first!\n/link your@email.com")
            return
        expenses = Expense.query.filter_by(user_id=user.id).order_by(Expense.date.desc()).limit(5).all()
        total = sum(e.amount for e in Expense.query.filter_by(user_id=user.id).all())
        if not expenses:
            await update.message.reply_text("No expenses yet!\nTry: spent 150 on lunch")
            return
        msg = f"📊 *Summary*\n💰 Total: ₹{total:.2f}\n\n🕐 Recent:\n"
        for e in expenses:
            msg += f"• {e.title} - ₹{e.amount:.2f} ({e.category})\n"
        await update.message.reply_text(msg, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    telegram_id = str(update.effective_user.id)
    amount, title = parse_expense(text)

    if amount is None:
        await update.message.reply_text("❓ Try: spent 150 on lunch\nOr /help")
        return

    from app import app, db, Expense, User
    with app.app_context():
        user = User.query.filter_by(telegram_id=telegram_id).first()
        if not user:
            await update.message.reply_text("❌ Please link first!\n/link your@email.com")
            return
        category = get_category(title)
        new_expense = Expense(
            title=title, amount=amount,
            category=category, date=datetime.utcnow(),
            user_id=user.id
        )
        db.session.add(new_expense)
        db.session.commit()
        await update.message.reply_text(
            f"✅ Logged!\n📝 {title.capitalize()}\n💰 ₹{amount:.2f}\n🏷️ {category}"
        )

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("link", link))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()