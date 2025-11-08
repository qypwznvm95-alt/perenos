cat > bot.py << 'EOF'
import logging
import os
import sqlite3
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, timedelta
import io
import asyncio

# Настройка бота
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = "8334498200:AAFafS7CMwYuFwMW5Ze4pFYH1YnZxhwSUV8"
ADMIN_CHAT_ID = "5533990703"
MANAGER_USERNAME = "@AUTOPRIMEmanager"
PDF_FILE = "catalog.pdf"

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_action TEXT,
            last_action_time DATETIME,
            manager_message_sent BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    conn.close()

def log_user_action(user_id, username, first_name, action):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (user_id, username, first_name, last_action, last_action_time) 
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, action, datetime.now()))
    conn.commit()
    conn.close()

def get_users_for_manager_message():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, username, first_name FROM users 
        WHERE manager_message_sent = FALSE 
        AND last_action_time > datetime('now', '-1 day')
    ''')
    users = cursor.fetchall()
    conn.close()
    return users

def mark_manager_message_sent(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET manager_message_sent = TRUE WHERE user_id = ?
    ''', (user_id,))
    conn.commit()
    conn.close()

async def send_manager_followup(application, user_id, username, first_name):
    try:
        manager_message = (
 f"👋 Привет, {first_name or 'друг'}!\n\n"
            f"Это {MANAGER_USERNAME} - менеджер AUTOPRIME.\n\n"
            "🔍 Вижу, что Вы интересовались нашим каталогом автомобилей. "
            "Хочу лично предложить Вам помощь в подборе авто!\n\n"
            "🚗 <b>Что я могу для Вас сделать:</b>\n"
            "• Подобрать автомобиль по Вашим параметрам\n"
            "• Ответить на все вопросы по покупке\n"
            "• Организовать полный цикл сделки\n"
            "• Проконсультировать по документам\n\n"
            "💬 <b>Напиши мне прямо сейчас:</b>\n"
            "• Telegram: @AUTOPRIMEmanager\n"
            "• WhatsApp: https://wa.me/79188999006\n\n"
            "Жду Вашего сообщения! 😊"
        )
        
        await application.bot.send_message(
            chat_id=user_id,
            text=manager_message,
            parse_mode='HTML'
        )
        
        mark_manager_message_sent(user_id)
        print(f"✅ Авто-сообщение менеджера отправлено пользователю {first_name} (ID: {user_id})")
        
    except Exception as e:
        print(f"❌ Ошибка отправки авто-сообщения пользователю {user_id}: {e}")

async def scheduled_manager_messages(context: ContextTypes.DEFAULT_TYPE):
    """Задача для автоматической рассылки"""
    try:
        print("🔍 Проверяю пользователей для авто-рассылки...")
        users = get_users_for_manager_message()
        
        if users:
            print(f"📤 Найдено {len(users)} пользователей для рассылки")
            
            for user_id, username, first_name in users:
                await send_manager_followup(context.application, user_id, username, first_name)
                await asyncio.sleep(2)  # Пауза между сообщениями
        else:
            print("✅ Нет новых пользователей для рассылки")
            
    except Exception as e:
        print(f"❌ Ошибка в scheduled_manager_messages: {e}")

def create_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/autoprimechannel")],
        [InlineKeyboardButton("👥 Подписаться на группу", url="https://t.me/autoprimepro")],
        [InlineKeyboardButton("💬 Написать в WhatsApp", url="https://wa.me/79188999006")],
        [InlineKeyboardButton("✍️ Написать в Telegram", url="https://t.me/AUTOPRIMEmanager")],
        [InlineKeyboardButton("📥 ПОЛУЧИТЬ КАТАЛОГ PDF", callback_data="get_catalog")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_admin_notification(application, message: str):
    try:
        await application.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message,
            parse_mode='HTML'
        )
        print("📢 Уведомление отправлено администратору")
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления: {e}")

async def send_pdf_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Логируем действие пользователя
    log_user_action(user.id, user.username, user.first_name, "requested_catalog")
    
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text="📥 <b>Спасибо! Отправляем каталог...</b>",
            parse_mode='HTML'
        )

        # Отправляем локальный PDF файл
        with open(PDF_FILE, 'rb') as pdf_file:
            await context.bot.send_document(
                chat_id=user.id,
                document=pdf_file,
                filename="Каталог AUTOPRIME до 160 л.с..pdf",
                caption="📋 <b>Каталог автомобилей до 160 л.с.</b>\n\n"
                       "🚗 Более 50 моделей от ведущих брендов\n"
                       "💰 Предложим лучшие цены на рынке\n" 
                       "⚡ Быстрая доставка\n\n"
                       "📄 Чистые документы\n\n"
                       "📞 По всем вопросам:\n"
                       "• <a href='https://t.me/AUTOPRIMEmanager'>Telegram менеджер</a>\n"
                       "• <a href='https://wa.me/79188999006'>WhatsApp менеджер</a>",
                parse_mode='HTML'
            )
        
        print(f"✅ PDF файл успешно отправлен пользователю {user.first_name}")
        
        # Уведомление администратору
        user_info = (
            f"👤 <b>{user.first_name or 'Не указано'}</b>\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"📛 Username: @{user.username or 'Не указан'}\n"
            f"🕐 Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
        )
        
        notification = (
            "📥 <b>ПОЛЬЗОВАТЕЛЬ ЗАПРОСИЛ КАТАЛОГ</b>\n\n"
            f"{user_info}\n"
            f"📲 <b>Действие:</b> Скачал каталог PDF\n"
            f"🔔 <b>Авто-сообщение:</b> Будет отправлено через 5 минут\n\n"
            f"💬 <b>Написать пользователю:</b>\n"
            f"• <a href='tg://user?id={user.id}'>Написать в Telegram</a>\n"
            f"• <a href='https://wa.me/79188999006'>Перейти в WhatsApp</a>"
        )
        await send_admin_notification(context.application, notification)
        
    except Exception as e:
        print(f"❌ Ошибка отправки PDF: {e}")
        await context.bot.send_message(
            chat_id=user.id,
            text="❌ Произошла ошибка при отправке каталога.\n\n"
                 "📞 <b>Свяжитесь с менеджером:</b>\n"
                 "• <a href='https://t.me/AUTOPRIMEmanager'>Telegram</a>\n"
                 "• <a href='https://wa.me/79188999006'>WhatsApp</a>",
            parse_mode='HTML'
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Логируем действие пользователя
    log_user_action(user.id, user.username, user.first_name, "started_bot")
    
    user_info = (
        f"👤 <b>{user.first_name or 'Не указано'}</b>\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📛 Username: @{user.username or 'Не указан'}\n"
        f"🌐 Язык: {user.language_code or 'Не указан'}\n"
        f"🕐 Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
    )
    
    welcome_text = (
        "🚗 AUTOPRIME - Ваш надежный партнер в мире экспорта автомобилей!\n\n"
        "✅ Быстрый и профессиональный подбор\n"
        "✅ Полная проверка авто перед покупкой\n"
        "✅ Гарантия юридической чистоты\n"
        "✅ Консультации экспертов\n\n"
        "📋 <b>Нажмите кнопку ниже чтобы получить каталог автомобилей до 160 л.с. в PDF</b>"
    )

    await update.message.reply_text(
        text=welcome_text,
        reply_markup=create_keyboard(),
        parse_mode='HTML'
    )
    
    notification = (
        "🚀 <b>НОВЫЙ ПОЛЬЗОВАТЕЛЬ</b>\n\n"
        f"{user_info}\n"
        f"📲 <b>Действие:</b> Запустил бота\n"
        f"🔔 <b>Авто-сообщение:</b> Будет отправлено через 5 минут"
    )
    await send_admin_notification(context.application, notification)
    
    print(f"👤 Пользователь {user.first_name} запустил бота")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    button_data = query.data
    
    print(f"🔄 Пользователь {user.first_name} нажал кнопку: {button_data}")
    
    if button_data == "get_catalog":
        await send_pdf_catalog(update, context)

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Логируем действие пользователя
    log_user_action(user.id, user.username, user.first_name, "used_catalog_command")
    
    print(f"📋 Пользователь {user.first_name} запросил каталог командой")
    
    user_info = (
        f"👤 <b>{user.first_name or 'Не указано'}</b>\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📛 Username: @{user.username or 'Не указан'}\n"
        f"🕐 Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
    )
    
    notification = (
        "🔘 <b>КОМАНДА ОТ ПОЛЬЗОВАТЕЛЯ</b>\n\n"
        f"{user_info}\n"
        f"📲 <b>Действие:</b> Использовал команду /catalog\n"
        f"🔔 <b>Авто-сообщение:</b> Будет отправлено через 5 минут\n\n"
        f"💬 <b>Написать пользователю:</b>\n"
        f"• <a href='tg://user?id={user.id}'>Написать в Telegram</a>\n"
        f"• <a href='https://wa.me/79188999006'>Перейти в WhatsApp</a>"
    )
    await send_admin_notification(context.application, notification)
    
    await send_pdf_catalog(update, context)

def main():
    print("✅ Бот запускается на Beget...")
    
    try:
        # Инициализируем базу данных
        init_db()
        print("📁 База данных пользователей инициализирована")
        
        # Создаем Application с JobQueue
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("catalog", catalog))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Настраиваем JobQueue для автоматической рассылки
        job_queue = application.job_queue
        job_queue.run_repeating(scheduled_manager_messages, interval=1800, first=10)  # Каждые 30 минут
        
        print("🤖 Бот AUTOPRIME запущен на Beget!")
        print("📢 Система уведомлений активирована")
        print("📁 Используется локальный PDF файл")
        print("🔔 Авто-рассылка менеджера активирована")
        print("⏰ Проверка новых пользователей каждые 30 минут")
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Критическая ошибка бота: {e}")

if __name__ == "__main__":
    main()
