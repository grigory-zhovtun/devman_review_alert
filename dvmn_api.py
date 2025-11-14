"""Клиент API для Devman.org.

Модуль содержит функции для работы с long-polling API Devman.org
получения уведомлений о проверке работ ученика.
"""

import requests


DVMN_URL = 'https://dvmn.org/api/user_reviews/'
DVMN_URL_LONG_POLLING = 'https://dvmn.org/api/long_polling/'
LONG_POLLING_TIMEOUT_SECONDS = 95


def fetch_reviews(timestamp, dvmn_token):
    """Получает уведомления о проверке работ через long-polling API.

    Args:
        timestamp: Временная метка для получения уведомлений с момента
                   последнего запроса. Если None, получает все уведомления.
        dvmn_token: Токен авторизации Devman.org API.

    Returns:
        dict: Ответ от API Devman.org со статусом и данными о проверках.
              Может содержать статус 'timeout' или данные о новых проверках.
    """
    headers = {
        "Authorization": f"Token {dvmn_token}",
    }
    params = {'timestamp': timestamp}

    response = requests.get(
        DVMN_URL_LONG_POLLING,
        headers=headers,
        timeout=LONG_POLLING_TIMEOUT_SECONDS,
        params=params
    )
    response.raise_for_status()
    return response.json()
