import os
from dotenv import load_dotenv

# Загружаем переменные окружения при импорте модуля
load_dotenv()

DVMN_URL = 'https://dvmn.org/api/user_reviews/'
DVMN_URL_LONG_POLLING = 'https://dvmn.org/api/long_polling/'

LONG_POLLING_TIMEOUT_SECONDS = 95
CHECK_INTERVAL_SECONDS = 300

DVMN_TOKEN = os.getenv('DEVMAN_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# ПОТОМ проверяем, что они не пустые
missing = []
if not DVMN_TOKEN:
    missing.append('DEVMAN_TOKEN')
if not TELEGRAM_TOKEN:
    missing.append('TELEGRAM_TOKEN')
if not TELEGRAM_CHAT_ID:
    missing.append('TELEGRAM_CHAT_ID')

if missing:
    raise ValueError(
        f"Отсутствуют обязательные переменные окружения: {', '.join(missing)}\n"
        f"Проверьте файл .env"
    )