# -*- coding: utf-8 -*-
import logging
import argparse
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from dvmn_api import fetch_reviews
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, CHECK_INTERVAL

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TG_CHAT_ID = TELEGRAM_CHAT_ID


async def check_reviews(context: ContextTypes.DEFAULT_TYPE) -> None:
    timestamp = context.job.data.get('timestamp', None)
    response_data = fetch_reviews(timestamp)

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

                await context.bot.send_message(chat_id=TG_CHAT_ID, text=message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Привет, {update.effective_user.first_name}!')


def main() -> None:
    global TG_CHAT_ID

    parser = argparse.ArgumentParser(
        description='Telegram bot for checking DVMN reviews'
    )
    parser.add_argument(
        '--chat_id',
        help='Telegram chat ID',
        default=TELEGRAM_CHAT_ID,
    )
    args = parser.parse_args()
    TG_CHAT_ID = args.chat_id

    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    application.add_handler(CommandHandler("start", start))

    job_queue = application.job_queue
    job_queue.run_repeating(check_reviews, interval=CHECK_INTERVAL, first=1, data={})

    application.run_polling()


if __name__ == '__main__':
    main()