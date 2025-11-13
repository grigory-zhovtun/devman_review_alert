import logging
import requests


DVMN_URL = 'https://dvmn.org/api/user_reviews/'
DVMN_URL_LONG_POLLING = 'https://dvmn.org/api/long_polling/'
LONG_POLLING_TIMEOUT_SECONDS = 95

def fetch_reviews(timestamp, dvmn_token):
    headers = {
        "Authorization": f"Token {dvmn_token}",
    }
    params = {'timestamp': timestamp}

    try:
        response = requests.get(
            DVMN_URL_LONG_POLLING,
            headers=headers,
            timeout=LONG_POLLING_TIMEOUT_SECONDS,
            params=params
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as err:
        status = err.response.status_code if err.response is not None else "unknown"
        body = err.response.text if err.response is not None else "no body"
        raise RuntimeError(f"HTTP error {status}: {body}") from err

    except requests.exceptions.ReadTimeout:
        return None

    except requests.exceptions.RequestException as err:
        logging.error(f"Network error: {err}")
        return None
