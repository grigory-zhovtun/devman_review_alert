import os
from dotenv import load_dotenv

# Загружаем переменные окружения при импорте модуля
load_dotenv()

DVMN_TOKEN = os.environ.get('DEVMAN_TOKEN')
DVMN_URL = 'https://dvmn.org/api/user_reviews/'
DVMN_URL_LONG_POLLING = 'https://dvmn.org/api/long_polling/'
POOLING_TIMEOUT = 95

if not DVMN_TOKEN:
    raise RuntimeError("Переменная окружения DEVMAN_TOKEN не найдена. Проверьте файл .env и загрузку окружения.")