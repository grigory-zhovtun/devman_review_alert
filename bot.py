# -*- coding: utf-8 -*-
import os
import time
import requests
from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import (
    CommandHandler, CallbackContext, Updater,
)
from dvmn_api import fetch_reviews

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 300


def check_reviews(context: CallbackContext) -> None:
    chat_id = context.job.context['chat_id']
    dvmn_token = context.job.context['dvmn_token']

    reviews = fetch_reviews(context.job.context.get('timestamp'), dvmn_token)

    if not reviews:
        return
    if reviews.get('status') == 'timeout':
        context.job.context['timestamp'] = reviews.get('timestamp_to_request')
        return

    context.job.context['timestamp'] = reviews.get('last_attempt_timestamp')
    new_attempts = reviews.get('new_attempts', [])

    for attempt in new_attempts:
        status = "К сожалению, в работе нашлись ошибки." \
            if attempt['is_negative'] \
            else "Преподавателю все понравилось!"
        message = f'У вас проверили работу "{attempt["lesson_title"]}"\n\n{status}\n\nСсылка: {attempt["lesson_url"]}'
        context.bot.send_message(chat_id=chat_id, text=message)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Привет, {update.effective_user.first_name}!')


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    while True:
        try:
            config = {
                'DVMN_TOKEN': os.getenv('DEVMAN_TOKEN'),
                'TELEGRAM_TOKEN': os.getenv('TELEGRAM_TOKEN'),
                'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID')
            }

            missing = [key for key, value in config.items() if not value]
            if missing:
                raise ValueError(f"Отсутствуют переменные: {', '.join(missing)}\nПроверьте .env")

            updater = Updater(token=config['TELEGRAM_TOKEN'])
            dispatcher = updater.dispatcher

            dispatcher.add_handler(CommandHandler("start", start))

            updater.job_queue.run_repeating(
                check_reviews,
                interval=CHECK_INTERVAL_SECONDS,
                first=1,
                context={'chat_id': config['TELEGRAM_CHAT_ID'], 'dvmn_token': config['DVMN_TOKEN']}
            )

            updater.start_polling()
            updater.idle()

        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Ошибка подключения: {e}. Перезапуск через 10 секунд...")
            time.sleep(10)
            continue
        except requests.exceptions.Timeout as e:
            logger.warning(f"Таймаут соединения: {e}. Перезапуск через 5 секунд...")
            time.sleep(5)
            continue
        except requests.exceptions.ReadTimeout as e:
            logger.warning(f"Таймаут чтения: {e}. Продолжаем работу...")
            time.sleep(5)
            continue
        except requests.exceptions.HTTPError as e:
            if hasattr(e, 'response') and e.response.status_code in [500, 502, 503, 504]:
                logger.warning(
                    f"Временная ошибка сервера ({e.response.status_code}): {e}. Перезапуск через 30 секунд...")
                time.sleep(30)
                continue
            else:
                logger.error(f"HTTP ошибка: {e}")
                raise

        except Exception as e:
            logger.exception(f"Критическая ошибка: {e}. Перезапуск через 30 секунд...")
            time.sleep(30)
            continue


if __name__ == '__main__':
    main()