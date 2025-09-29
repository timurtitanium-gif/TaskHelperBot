# taskhelper_bot.py
import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# --- Инициализация базы данных ---
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    done INTEGER DEFAULT 0
)
""")
conn.commit()

# --- Команды бота ---
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Я TaskHelper бот.\n"
        "Используйте команды:\n"
        "/add <задача> - добавить задачу\n"
        "/list - показать задачи\n"
        "/done <номер> - отметить задачу выполненной\n"
        "/delete <номер> - удалить задачу"
    )

def add_task(update: Update, context: CallbackContext):
    description = " ".join(context.args)
    if description:
        cursor.execute("INSERT INTO tasks (description) VALUES (?)", (description,))
        conn.commit()
        update.message.reply_text(f"Задача добавлена: {description}")
    else:
        update.message.reply_text("Введите описание задачи после команды /add")

def list_tasks(update: Update, context: CallbackContext):
    cursor.execute("SELECT id, description, done FROM tasks")
    tasks = cursor.fetchall()
    if tasks:
        msg = ""
        for task in tasks:
            status = "✅" if task[2] else "❌"
            msg += f"{task[0]}. {task[1]} [{status}]\n"
        update.message.reply_text(msg)
    else:
        update.message.reply_text("Список задач пуст.")

def done_task(update: Update, context: CallbackContext):
    if context.args and context.args[0].isdigit():
        task_id = int(context.args[0])
        cursor.execute("UPDATE tasks SET done=1 WHERE id=?", (task_id,))
        conn.commit()
        update.message.reply_text(f"Задача {task_id} отмечена как выполненная.")
    else:
        update.message.reply_text("Введите номер задачи после команды /done")

def delete_task(update: Update, context: CallbackContext):
    if context.args and context.args[0].isdigit():
        task_id = int(context.args[0])
        cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        update.message.reply_text(f"Задача {task_id} удалена.")
    else:
        update.message.reply_text("Введите номер задачи после команды /delete")

# --- Основная функция ---
def main():
    TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"  # вставьте сюда токен вашего бота
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add_task))
    dp.add_handler(CommandHandler("list", list_tasks))
    dp.add_handler(CommandHandler("done", done_task))
    dp.add_handler(CommandHandler("delete", delete_task))

    print("Бот запущен...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
