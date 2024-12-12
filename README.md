QR Code Generator Bot

Welcome to the QR Code Generator Bot! This bot allows users to generate QR codes by simply sending a link. It also includes a feature to contact the developer directly via Telegram.

Features

Generate QR codes for any link you send.

Inline keyboard button to contact the developer.

Friendly loading animation while generating QR codes.

Prerequisites

Python 3.9 or higher installed on your system.

Install the required Python libraries:

pip install python-telegram-bot[qrcode] pillow

A Telegram bot token. You can create a bot and obtain the token from BotFather.

Setup Instructions

1. Clone the Repository

git clone https://github.com/abhinai2244/qr-code-generator-bot.git
cd qr-code-generator-bot

2. Update Bot Token and Developer Username

Edit the TOKEN and OWNER_USERNAME variables in the script with your Telegram bot token and your username:

TOKEN = 'your-telegram-bot-token'
OWNER_USERNAME = 'your-telegram-username'  # Without the @ symbol

3. Run the Bot

Start the bot by running the script:

python3 bot.py

You should see the following message:

🤖 Bot is running...

How to Use

Start the bot by sending /start in a chat with it.

Send a link (e.g., https://www.example.com) to generate a QR code.

The bot will:

Display a loading animation.

Send back a QR code for your link.

Use the "📩 Contact Developer" button to contact the developer directly if needed.
