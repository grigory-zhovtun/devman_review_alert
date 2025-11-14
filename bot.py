# -*- coding: utf-8 -*-
"""Telegram бот для уведомлений о проверке работ на Devman.org.

Бот использует long-polling API Devman.org для получения уведомлений
о проверке работ и отправляет их в указанный Telegram чат.
"""

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
    """Проверяет наличие новых ревью и отправляет уведомления.

    Args:
        context: Контекст CallbackContext от telegram.ext
    """
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
        is_negative = attempt['is_negative']
        status = ("К сожалению, в работе нашлись ошибки."
                  if is_negative
                  else "Преподавателю все понравилось!")
        message = (f'У вас проверили работу "{attempt["lesson_title"]}"'
                   f'\n\n{status}\n\nСсылка: {attempt["lesson_url"]}')
        context.bot.send_message(chat_id=chat_id, text=message)


def start(update: Update, context: CallbackContext) -> None:
    """Обрабатывает команду /start.

    Args:
        update: Объект Update от Telegram
        context: Контекст CallbackContext от telegram.ext
    """
    update.message.reply_text(f'Привет, {update.effective_user.first_name}!')


def main() -> None:
    """Основная функция для запуска Telegram бота.

    Загружает конфигурацию, настраивает обработчики команд
    и запускает бота с планировщиком проверки ревью.
    """
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

            missing_keys = [key for key, value in config.items() if not value]
            if missing_keys:
                error_msg = (f"Отсутствуют переменные: "
                             f"{', '.join(missing_keys)}\nПроверьте .env")
                raise ValueError(error_msg)

            updater = Updater(token=config['TELEGRAM_TOKEN'])
            dispatcher = updater.dispatcher

            dispatcher.add_handler(CommandHandler("start", start))

            job_context = {
                'chat_id': config['TELEGRAM_CHAT_ID'],
                'dvmn_token': config['DVMN_TOKEN']
            }
            updater.job_queue.run_repeating(
                check_reviews,
                interval=CHECK_INTERVAL_SECONDS,
                first=1,
                context=job_context
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
