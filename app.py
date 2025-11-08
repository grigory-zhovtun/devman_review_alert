import time
import logging

import requests
import os
from dotenv import load_dotenv


load_dotenv()
token = os.environ.get('DEVMAN_TOKEN')
url = 'https://dvmn.org/api/user_reviews/'
url_long_pooling = 'https://dvmn.org/api/long_polling/'
POOLING_TIMEOUT = 95

if not token:
    raise RuntimeError("Переменная окружения DEVMAN_TOKEN не найдена. Проверьте файл .env и загрузку окружения.")

headers = {
    "Authorization": f"Token {token}",
}

while True:
    try:
        response = requests.get(url_long_pooling, headers=headers, timeout=POOLING_TIMEOUT)
        response.raise_for_status()
        print(response.json())
    except requests.exceptions.HTTPError as err:
        status = err.response.status_code if err.response is not None else "unknown"
        body = err.response.text if err.response is not None else "no body"
        raise RuntimeError(f"HTTP error {status}: {body}") from err
    except requests.exceptions.RequestException as err:
        logging.error(f"Network error: {err}")
        time.sleep(5)