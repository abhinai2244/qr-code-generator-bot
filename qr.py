import os
import io
import qrcode
import sqlite3
from flask import Flask, request, send_file, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pptx import Presentation
from PIL import Image
import subprocess
import win32com.client  # For PowerPoint COM automation
import threading
import requests

# Telegram Bot Token and Owner Information
TOKEN = '7608849767:AAGvXT5Y_GfuZRxZURDuds9JW4g4So8eE1U'  # Replace with your bot token
OWNER_USERNAME = '@clutch008'
OWNER_USER_ID = '5756495153'  # You can use either username or user ID

# SQLite database setup for logging
conn = sqlite3.connect('logs.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS logs (user_id TEXT, username TEXT, action TEXT, timestamp TEXT)''')
conn.commit()

# Initialize Flask App
app = Flask(__name__)

# Route 1: QR Code Generation via Flask
@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    if 'link' not in request.form:
        return jsonify({"error": "No link provided"}), 400

    link = request.form['link']
    if not link.startswith("http"):
        return jsonify({"error": "Invalid link format. Provide a valid URL."}), 400

    # Generate QR code
    qr = qrcode.make(link)
    bio = io.BytesIO()
    qr.save(bio, 'PNG')
    bio.seek(0)
    return send_file(bio, mimetype='image/png', as_attachment=True, download_name='qr_code.png')

# Route 2: Image Compression
@app.route('/compress_image', methods=['POST'])
def compress_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']
    img = Image.open(file)
    bio = io.BytesIO()
    img.save(bio, 'JPEG', quality=20)  # Compress to 20% quality
    bio.seek(0)
    return send_file(bio, mimetype='image/jpeg', as_attachment=True, download_name='compressed_image.jpg')

# Route 3: PPTX to PDF Conversion using PowerPoint
@app.route('/pptx_to_pdf', methods=['POST'])
def pptx_to_pdf():
    if 'pptx_file' not in request.files:
        return jsonify({"error": "No PPTX file provided"}), 400

    file = request.files['pptx_file']
    pptx_bio = io.BytesIO()

    try:
        # Save the uploaded PPTX file temporarily
        file.save('ppt_temp.pptx')

        # Convert PPTX to PDF using PowerPoint
        convert_pptx_to_pdf('ppt_temp.pptx')

        # Read the generated PDF
        with open('ppt_temp.pdf', 'rb') as pdf_file:
            pptx_bio.write(pdf_file.read())
        pptx_bio.seek(0)

        # Send the PDF back to the user
        return send_file(pptx_bio, mimetype='application/pdf', as_attachment=True, download_name='presentation.pdf')

    except Exception as e:
        notify_owner(f"Error in PPTX to PDF conversion: {str(e)}")
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500

def convert_pptx_to_pdf(input_file):
    output_file = 'ppt_temp.pdf'
    try:
        # Initialize PowerPoint application
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        powerpoint.Visible = 1  # Make PowerPoint visible (optional)

        # Open the PPTX file
        presentation = powerpoint.Presentations.Open(os.path.abspath(input_file))

        # Save the presentation as PDF
        presentation.SaveAs(os.path.abspath(output_file), 32)  # 32 is the PowerPoint constant for PDF format
        presentation.Close()

        powerpoint.Quit()  # Quit the PowerPoint application

    except Exception as e:
        raise Exception(f"Error converting PPTX to PDF: {str(e)}")

def notify_owner(message):
    """Send an error message to the owner's Telegram account."""
    from telegram import Bot

    bot = Bot(token=TOKEN)
    bot.send_message(chat_id=OWNER_USER_ID, text=message)

# Telegram Bot Functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "👋 Welcome to the QR Code Generator Bot!\n"
        "1.🔗 Send me any link, and I'll create a QR code for you.\n"
        "2.🖼️ Send an image to compress it.\n"
        "3.📂 Send a PPTX file to convert it to PDF.\n"
        "4.📝 Send me any text, and I'll generate a QR code with that text.\n"
        "5.🔗 Send me a long URL, and I can shorten it for you.\n"
        "Type /help for more info.\n🥶"
    )
    await update.message.reply_text(welcome_message)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_message = (
        "Here are the available commands:\n"
        "/start - Start the bot and get a welcome message\n"
        "/help - Get help with the bot's features\n"
        "/view_logs - View recent logs (only for the bot owner)\n"
        "Send a link to generate a QR code\n"
        "Send an image to compress it\n"
        "Send a PPTX file to convert it to PDF\n"
        "Send any text, and I'll create a QR code for that text."
    )
    await update.message.reply_text(help_message)

async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    try:
        qr = qrcode.make(text)
        bio = io.BytesIO()
        qr.save(bio, 'PNG')
        bio.seek(0)

        # Log the action in the database
        user_id = update.message.from_user.id
        username = update.message.from_user.username
        action = "Generated QR Code"
        timestamp = update.message.date.isoformat()
        cursor.execute("INSERT INTO logs (user_id, username, action, timestamp) VALUES (?, ?, ?, ?)", (user_id, username, action, timestamp))
        conn.commit()

        # Send the QR code image
        await update.message.reply_photo(photo=bio, caption='✅ Here is your QR code!')
    except Exception as e:
        await update.message.reply_text('❌ Error generating QR code. Ensure the input is valid text or URL.')
        notify_owner(f"Error generating QR code: {str(e)}")

async def compress_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo = await update.message.photo[-1].get_file()
    file_bio = io.BytesIO()
    await photo.download_to_memory(file_bio)

    img = Image.open(file_bio)
    bio = io.BytesIO()
    img.save(bio, 'JPEG', quality=20)
    bio.seek(0)

    await update.message.reply_document(document=bio, filename='compressed_image.jpg', caption='✅ Your compressed image.')

async def shorten_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("❌ Please provide a URL to shorten.")
        return

    url = context.args[0]
    try:
        response = requests.get(f'https://api.shrtco.de/v2/shorten?url={url}')
        data = response.json()
        if data['ok']:
            short_url = data['result']['short_link']
            await update.message.reply_text(f"✅ Shortened URL: {short_url}")
        else:
            await update.message.reply_text("❌ Error shortening URL.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def view_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.username != OWNER_USERNAME:
        await update.message.reply_text("❌ You do not have permission to view the logs.")
        return
    
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10")
    logs = cursor.fetchall()
    log_text = "\n".join([f"{log[3]} - {log[2]}: {log[4]}" for log in logs])
    await update.message.reply_text(f"Recent logs:\n{log_text}")

def start_telegram_bot():
    application = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("view_logs", view_logs))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_qr))
    application.add_handler(MessageHandler(filters.PHOTO, compress_image))
    application.add_handler(MessageHandler(filters.Document.MimeType("application/vnd.ms-powerpoint") | filters.Document.MimeType("application/vnd.openxmlformats-officedocument.presentationml.presentation"), pptx_to_pdf))
    application.add_handler(CommandHandler("shorten", shorten_url))  # Add shorten URL command

    print("🤖 Telegram Bot is running...")
    application.run_polling()

# Start Flask and Telegram bot
if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
    flask_thread.start()

    # Run Telegram bot
    start_telegram_bot()
