import time
import logging
import requests
from config import  DVMN_TOKEN, POOLING_TIMEOUT, DVMN_URL_LONG_POLLING


def fetch_reviews():
    timestamp = None

    headers = {
        "Authorization": f"Token {DVMN_TOKEN}",
    }

    while True:
        try:
            response = requests.get(
                DVMN_URL_LONG_POLLING,
                headers=headers,
                timeout=POOLING_TIMEOUT,
                params={'timestamp': timestamp}
            )
            response.raise_for_status()
            response_data = response.json()

            if response_data.get('status') == 'timeout':
                timestamp = response_data.get('timestamp_to_request')
            else:
                timestamp = response_data.get('last_attempt_timestamp')
            return response_data
        except requests.exceptions.HTTPError as err:
            status = err.response.status_code if err.response is not None else "unknown"
            body = err.response.text if err.response is not None else "no body"
            raise RuntimeError(f"HTTP error {status}: {body}") from err
        except requests.exceptions.ReadTimeout as err:
            continue
        except requests.exceptions.RequestException as err:
            logging.error(f"Network error: {err}")
            time.sleep(5)
