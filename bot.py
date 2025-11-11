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
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, CHECK_INTERVAL_SECONDS

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def check_reviews(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.data.get('chat_id')

    if not chat_id:
        logger.error("No chat ID in job context")
        return

    try:
        chat_id = context.job.data.get('chat_id')
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

                    await context.bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logger.exception(f"Ошибка при проверке ревью: {e}")

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⚠️ Ошибка бота: {e}"
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Привет, {update.effective_user.first_name}!')


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Telegram bot for checking DVMN reviews'
    )
    parser.add_argument(
        '--chat_id',
        help='Telegram chat ID',
        default=TELEGRAM_CHAT_ID,
    )
    args = parser.parse_args()

    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    application.add_handler(CommandHandler("start", start))

    job_queue = application.job_queue
    job_queue.run_repeating(
        check_reviews,
        interval=CHECK_INTERVAL_SECONDS,
        first=1,
        data={'chat_id': args.chat_id}
    )

    application.run_polling()


if __name__ == '__main__':
    main()