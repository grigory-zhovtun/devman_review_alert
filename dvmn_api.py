import requests


DVMN_URL = 'https://dvmn.org/api/user_reviews/'
DVMN_URL_LONG_POLLING = 'https://dvmn.org/api/long_polling/'
LONG_POLLING_TIMEOUT_SECONDS = 95


def fetch_reviews(timestamp, dvmn_token):
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
