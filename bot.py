import sqlite3
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, ContextTypes)

# Replace with your actual Telegram bot token
TOKEN = "7836477731:AAEj_WN10bTQJ3q3EmmZtXgPljEI-YiEnBc"
PROMO_MESSAGE = "\n\n📢 *Made by Pharmacy Revolutionary!*\nJoin 👉 @PHARMACYREVOLUTIONARY | @DISCUSSIONREVOLUTIONARY"

user_scores = {}
active_quizzes = {}

# Setup DB

def create_database():
    conn = sqlite3.connect('pharmacology.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mcqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            correct_answer TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

# Get random MCQ

def get_random_mcq():
    conn = sqlite3.connect('pharmacology.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mcqs ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'id': row[0],
            'question': row[1],
            'options': [row[2], row[3], row[4], row[5]],
            'answer': row[6]
        }
    return None

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to *Pharmacology Buddy*!\nUse /battle to start a quiz battle!" + PROMO_MESSAGE, parse_mode="Markdown")

# /battle command
async def battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in active_quizzes:
        await update.message.reply_text("⚠️ A quiz is already running in this group!")
        return

    await update.message.reply_text("🚀 Starting *Pharmacology Battle*...", parse_mode="Markdown")
    active_quizzes[chat_id] = True
    user_scores[chat_id] = {}

    for i in range(26):
        await send_mcq(update, context, chat_id)
        await context.application.create_task(asyncio.sleep(30))

    await show_leaderboard(update, context, chat_id)
    del active_quizzes[chat_id]

# Send MCQ
async def send_mcq(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id):
    mcq = get_random_mcq()
    if not mcq:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ No MCQs found.")
        return

    buttons = [
        [InlineKeyboardButton(text=opt, callback_data=opt)] for opt in mcq['options']
    ]
    context.chat_data['answer'] = mcq['answer']
    context.chat_data['answered'] = set()

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"❓ *{mcq['question']}*",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

# Handle answers
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    await query.answer()

    if user.id in context.chat_data.get('answered', set()):
        return

    selected = query.data
    correct = context.chat_data.get('answer', '')

    if selected == correct:
        score = user_scores.setdefault(chat_id, {}).get(user.full_name, 0) + 1
        user_scores[chat_id][user.full_name] = score
        await query.edit_message_text(f"✅ *{user.full_name}* answered correctly!\n+1 Point!" + PROMO_MESSAGE, parse_mode="Markdown")
    else:
        await query.edit_message_text(f"❌ *{user.full_name}* was wrong. Correct: *{correct}*" + PROMO_MESSAGE, parse_mode="Markdown")

    context.chat_data['answered'].add(user.id)

# Show leaderboard
async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id=None):
    chat_id = chat_id or update.effective_chat.id
    scores = user_scores.get(chat_id, {})
    if not scores:
        await context.bot.send_message(chat_id=chat_id, text="No scores to show yet.")
        return

    leaderboard = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    text = "🏆 *Leaderboard* 🏆\n"
    for i, (user, score) in enumerate(leaderboard, start=1):
        text += f"{i}. {user} - {score} pts\n"

    await context.bot.send_message(chat_id=chat_id, text=text + PROMO_MESSAGE, parse_mode="Markdown")

# Run
import asyncio

def main():
    logging.basicConfig(level=logging.INFO)
    create_database()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("battle", battle))
    app.add_handler(CallbackQueryHandler(handle_answer))

    print("🤖 Pharmacology Buddy is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
