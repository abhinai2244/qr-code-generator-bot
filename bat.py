from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Define a command handler for the start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your bot. How can I assist you today? developed by 💀 Abhinai 💀')

# Define a message handler that echoes back the user's message
def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)

# Main function to run the bot
def main() -> None:
    # Replace 'YOUR_TOKEN' with your actual bot token from Telegram
    updater = Updater("7969617788:AAHcahrOow6vnEndAMsuXEmMoAoiHvK1KfI")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the command and message handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop (like Ctrl+C)
    updater.idle()

if name == 'main':
    main()
