# -*- coding: utf-8 -*-
import os
import requests
from dotenv import load_dotenv
import logging
import argparse
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from dvmn_api import fetch_reviews

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 300


def load_config():
    load_dotenv()

    config = {
        'DVMN_TOKEN': os.getenv('DEVMAN_TOKEN'),
        'TELEGRAM_TOKEN': os.getenv('TELEGRAM_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID')
    }

    missing = [key for key, value in config.items() if not value]

    if missing:
        raise ValueError(
            f"Отсутствуют обязательные переменные окружения: {', '.join(missing)}\n"
            f"Проверьте файл .env"
        )

    return config


async def check_reviews(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.data.get('chat_id')
    dvmn_token = context.job.data.get('dvmn_token')

    if not chat_id:
        logger.error("No chat ID in job context")
        return

    chat_id = context.job.data.get('chat_id')
    timestamp = context.job.data.get('timestamp', None)

    try:
        response_data = fetch_reviews(timestamp, dvmn_token)
    except requests.exceptions.ReadTimeout:
        return

    if response_data:
        if response_data.get('status') == 'timeout':
            context.job.data['timestamp'] = response_data.get('timestamp_to_request')
        else:
            context.job.data['timestamp'] = response_data.get('last_attempt_timestamp')
            new_attempts = response_data.get('new_attempts', [])

            for attempt in new_attempts:
                lesson_title = attempt['lesson_title']
                is_negative = attempt['is_negative']
                lesson_url = attempt['lesson_url']

                status_message = (
                    "К сожалению, в работе нашлись ошибки."
                    if is_negative
                    else "Преподавателю все понравилось, можно приступать к следующему уроку!"
                )

                message = (
                    f'У вас проверили работу "{lesson_title}"\n\n'
                    f'{status_message}\n\n'
                    f'Ссылка на урок: {lesson_url}'
                )

                await context.bot.send_message(chat_id=chat_id, text=message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Привет, {update.effective_user.first_name}!')


def main() -> None:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    try:
        config = load_config()
        parser = argparse.ArgumentParser(description='Telegram bot for checking DVMN reviews')
        parser.add_argument('--chat_id', help='Telegram chat ID', default=config['TELEGRAM_CHAT_ID'])
        args = parser.parse_args()

        application = (
            Application.builder()
            .token(config['TELEGRAM_TOKEN'])
            .concurrent_updates(True)
            .build()
        )

        application.add_handler(CommandHandler("start", start))

        job_queue = application.job_queue
        job_queue.run_repeating(
            check_reviews,
            interval=CHECK_INTERVAL_SECONDS,
            first=1,
            data={'chat_id': args.chat_id, 'dvmn_token': config['DVMN_TOKEN']}
        )

        application.run_polling()

    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
        raise


if __name__ == '__main__':
    main()