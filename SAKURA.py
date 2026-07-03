# -*- coding: utf-8 -*-
import os
import re
import sqlite3
import datetime
import telebot
from telebot import types
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

# Initialize Telebot
bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None

# Initialize Groq
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

DB_FILE = "sakura_knowledge.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS chats (chat_id TEXT PRIMARY KEY, name TEXT, type TEXT)")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT,
        msg_id TEXT,
        timestamp TEXT,
        text TEXT,
        keywords TEXT,
        insight TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_memory(chat_id, msg_id, text, keywords, insight=""):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    ts = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO memories (chat_id, msg_id, timestamp, text, keywords, insight) VALUES (?, ?, ?, ?, ?, ?)",
        (str(chat_id), str(msg_id), ts, text, keywords, insight)
    )
    conn.commit()
    conn.close()

def fetch_memories(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT text, timestamp, insight FROM memories WHERE chat_id = ? ORDER BY id DESC LIMIT 20", (str(chat_id),))
    rows = cursor.fetchall()
    conn.close()
    return [{"text": r[0], "date": r[1], "insight": r[2]} for r in rows]

def ask_groq(prompt):
    if not client:
        return "🌸 Ошибка: GROQ_API_KEY не настроен."
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"🌸 Ошибка ИИ: {str(e)}"

if bot:
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "🌸 S.A.K.U.R.A. на базе Groq запущена! Пиши свои мысли или задавай вопросы.")

    @bot.message_handler(func=lambda m: True)
    def handle_text(message):
        text = message.text
        chat_id = message.chat.id
        
        if "?" in text:
            # RAG Mode
            mems = fetch_memories(chat_id)
            context = "\n".join([f"- {m['text']}" for m in mems])
            prompt = f"Ты S.A.K.U.R.A. Ответь на вопрос: '{text}', используя память: {context}. Будь вежливой, используй эмодзи 🌸."
            reply = ask_groq(prompt)
            bot.reply_to(message, reply)
        else:
            # Save Mode
            mems = fetch_memories(chat_id)
            context = "\n".join([f"- {m['text']}" for m in mems[:5]])
            prompt = f"Ты S.A.K.U.R.A. Пользователь записал мысль: '{text}'. Дай краткий инсайт (1-2 предл), сравнив с прошлым: {context}. Начни с 🌸."
            insight = ask_groq(prompt)
            save_memory(chat_id, message.message_id, text, "", insight)
            bot.reply_to(message, insight)

if __name__ == "__main__":
    init_db()
    print("🌸 S.A.K.U.R.A. (Groq Edition) is running...")
    if bot:
        bot.infinity_polling()
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

DB_FILE = "sakura_knowledge.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS chats (chat_id TEXT PRIMARY KEY, name TEXT, type TEXT)")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT,
        msg_id TEXT,
        timestamp TEXT,
        text TEXT,
        keywords TEXT,
        insight TEXT
    )
    """
    )
    conn.commit()
    conn.close()

def save_memory(chat_id, msg_id, text, keywords, insight=""):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    ts = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO memories (chat_id, msg_id, timestamp, text, keywords, insight) VALUES (?, ?, ?, ?, ?, ?)",
        (str(chat_id), str(msg_id), ts, text, keywords, insight)
    )
    conn.commit()
    conn.close()

def fetch_memories(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT text, timestamp, insight FROM memories WHERE chat_id = ? ORDER BY id DESC LIMIT 20", (str(chat_id),))
    rows = cursor.fetchall()
    conn.close()
    return [{"text": r[0], "date": r[1], "insight": r[2]} for r in rows]

def ask_groq(prompt):
    if not client:
        return "🌸 Ошибка: GROQ_API_KEY не настроен."
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"🌸 Ошибка ИИ: {str(e)}"

if bot:
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "🌸 S.A.K.U.R.A. на базе Groq запущена! Пиши свои мысли или задавай вопросы.")

    @bot.message_handler(func=lambda m: True)
    def handle_text(message):
        text = message.text
        chat_id = message.chat.id
        
        if "?" in text:
            # RAG Mode
            mems = fetch_memories(chat_id)
            context = "\n".join([f"- {m['text']}" for m in mems])
            prompt = f"Ты S.A.K.U.R.A. Ответь на вопрос: '{text}', используя память: {context}. Будь вежливой, используй эмодзи 🌸."
            reply = ask_groq(prompt)
            bot.reply_to(message, reply)
        else:
            # Save Mode
            mems = fetch_memories(chat_id)
            context = "\n".join([f"- {m['text']}" for m in mems[:5]])
            prompt = f"Ты S.A.K.U.R.A. Пользователь записал мысль: '{text}'. Дай краткий инсайт (1-2 предл), сравнив с прошлым: {context}. Начни с 🌸."
            insight = ask_groq(prompt)
            save_memory(chat_id, message.message_id, text, "", insight)
            bot.reply_to(message, insight)

if __name__ == "__main__":
    init_db()
    print("🌸 S.A.K.U.R.A. (Groq Edition) is running...")
    if bot:
        bot.infinity_polling()

