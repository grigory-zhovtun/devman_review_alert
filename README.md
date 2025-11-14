# Devman Review Alert Bot

This Python script continuously checks for new code reviews on the [Devman.org](https://dvmn.org/) platform and sends timely notifications to a specified Telegram chat.

---

## Features

- **Long Polling**: Uses the Devman API's long polling mechanism for instant notifications without constant spam.
- **Telegram Integration**: Sends clear, formatted messages to a Telegram user or group.
- **Resilient**: Handles network errors and API timeouts gracefully.
- **Configurable**: All essential parameters (tokens, chat ID) are configured via environment variables or command-line arguments, not hardcoded.

---

## Prerequisites

- Python 3.8 or newer
- A `requirements.txt` file is provided to manage project dependencies.

---

## Installation and Setup

1.  **Clone the repository**
    ```bash
    git clone <your-repository-url>
    cd devman_review_alert
    ```

2.  **Create and activate a virtual environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate       # Linux/macOS
    .venv\Scripts\activate        # Windows
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables**
    Create a `.env` file in the project root. You can copy the provided `.env.example` if it exists.
    ```dotenv
    DEVMAN_TOKEN=your_devman_api_token
    TELEGRAM_TOKEN=your_telegram_bot_token
    TELEGRAM_CHAT_ID=your_telegram_chat_id
    ```

---

## Environment Variables

The application requires the following environment variables:

-   `DEVMAN_TOKEN`: Your personal Devman API token. You can get it from [this page](https://dvmn.org/api/docs/#authentication).
-   `TELEGRAM_TOKEN`: The token for your Telegram bot. Create a bot by talking to [@BotFather](https://t.me/BotFather) on Telegram.
-   `TELEGRAM_CHAT_ID`: The ID of the chat where the bot will send notifications. You can get your ID by messaging a bot like [@userinfobot](https://t.me/userinfobot).

---

## Usage

To start the bot, run the `bot.py` script from your terminal:

```bash
python bot.py
```

The bot will start polling for new reviews immediately.

---

## Example Notification

When a review is submitted, you will receive a message like this:

> У вас проверили работу "Название Урока"
>
> Преподавателю все понравилось, можно приступать к следующему уроку!
>
> Ссылка на урок: https://dvmn.org/lessons/.....

---

## Notes

-   The script is designed to run continuously. If it stops due to a critical error, it will need to be restarted manually.
-   The polling interval and timeout settings can be adjusted in the `config.py` file if needed.
