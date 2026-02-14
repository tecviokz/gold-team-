import os
import threading
import logging
from flask import Flask, render_template_string

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Создаем Flask приложение
app = Flask(__name__)

# Функция для запуска бота в отдельном потоке
def run_telegram_bot():
    try:
        import telegram_bot
        logging.info("Запуск Telegram бота...")
        telegram_bot.run_bot()
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")

# HTML шаблон для главной страницы
HOME_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Narkoz Team Bot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #121212;
            color: #ffffff;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        .container {
            max-width: 800px;
            padding: 20px;
        }
        h1 {
            color: #4CAF50;
            margin-bottom: 20px;
        }
        p {
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .status {
            background-color: #1e1e1e;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            border-left: 4px solid #4CAF50;
        }
        .tg-link {
            display: inline-block;
            background-color: #0088cc;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
            font-weight: bold;
            transition: background-color 0.3s;
        }
        .tg-link:hover {
            background-color: #006699;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Narkoz Team Бот</h1>
        <p>
            Это серверная часть Telegram-бота Narkoz Team, который помогает управлять очередью номеров и другими задачами.
        </p>
        <div class="status">
            <p>Статус: <span style="color: #4CAF50;">✓ Запущен</span></p>
            <p>Бот работает в Telegram</p>
        </div>
        <a href="https://t.me/narkoz_team_bot" class="tg-link">Открыть в Telegram</a>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_PAGE)

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем Flask приложение
    logging.info("Запуск веб-сервера...")
    app.run(host='0.0.0.0', port=5000)