
import qrcode
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = '7969617788:AAHcahrOow6vnEndAMsuXEmMoAoiHvK1KfI'  # Replace with your actual bot token
OWNER_USERNAME = 'clutch008'  # Replace with your Telegram username (without @)

def main() -> None:
    # Initialize the application
    application = ApplicationBuilder().token(TOKEN).build()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        welcome_message = (
            "👋 Welcome to the QR Code Generator Bot!\n"
            "🔗 Send me any link, and I'll create a QR code for you.\n"
            "💡 Example: Just send 'https://www.example.com'"
        )
        await update.message.reply_text(welcome_message)

    async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        link = update.message.text
        try:
            qr = qrcode.make(link)
            bio = io.BytesIO()
            bio.name = 'qr.png'
            qr.save(bio, 'PNG')
            bio.seek(0)

            # Create an inline button to DM the owner
            keyboard = [[InlineKeyboardButton("📩 Contact Developer", url=f"https://t.me/{OWNER_USERNAME}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send a loading animation/gif
            await update.message.reply_animation(animation='https://media.giphy.com/media/8TIbelFjFXjIJ0Zg1l/giphy.gif?cid=790b7611un1wylv0qh1m147uu0vqn5kknc8fyqhz4wc8fq8g&ep=v1_gifs_search&rid=giphy.gif&ct=g', caption="Generating your QR code, please wait... 🛠️")

            # Send the QR code image
            await update.message.reply_photo(photo=bio, caption='✅ Here is your QR code!\n\nSupport the developer by clicking below:', reply_markup=reply_markup)
        except Exception as e:
            await update.message.reply_text('❌ There was an error generating the QR code. Please try again.')

    # Register the command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_qr))

    # Start the bot
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()

