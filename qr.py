import os
import io
import qrcode
from flask import Flask, request, send_file, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pptx import Presentation
from PIL import Image
import subprocess
import win32com.client  # For PowerPoint COM automation

# Telegram Bot Token and Owner Information
TOKEN = '7608849767:AAGvXT5Y_GfuZRxZURDuds9JW4g4So8eE1U'
OWNER_USERNAME = '@clutch008'
OWNER_USER_ID = '5756495153'  # You can use either username or user ID

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
        "NOTICE:DONT TYPE MESSG IT WILL CREATE QR CODE FOR THAT\n🥶"
    )
    await update.message.reply_text(welcome_message)

async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    link = update.message.text
    try:
        qr = qrcode.make(link)
        bio = io.BytesIO()
        qr.save(bio, 'PNG')
        bio.seek(0)

        # Send the QR code image
        await update.message.reply_photo(photo=bio, caption='✅ Here is your QR code!')
    except Exception as e:
        await update.message.reply_text('❌ Error generating QR code. Ensure the input is a valid URL.')
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

async def pptx_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if the document is a PPTX file
    if not update.message.document.file_name.lower().endswith('.pptx'):
        await update.message.reply_text('❌ Please send a valid PPTX file.')
        return

    doc = await update.message.document.get_file()
    file_bio = io.BytesIO()
    await doc.download_to_memory(file_bio)

    try:
        # Save the file temporarily and convert
        with open('ppt_temp.pptx', 'wb') as temp_file:
            temp_file.write(file_bio.getvalue())

        # Convert PPTX to PDF using PowerPoint
        convert_pptx_to_pdf('ppt_temp.pptx')

        # Send the converted PDF
        with open('ppt_temp.pdf', 'rb') as pdf_file:
            await update.message.reply_document(document=pdf_file, filename='presentation.pdf', caption='✅ Your converted PDF.')

    except Exception as e:
        await update.message.reply_text(f'❌ Error converting PPTX to PDF: {str(e)}')
        notify_owner(f"Error converting PPTX to PDF: {str(e)}")

# Register the handler
def start_telegram_bot():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_qr))
    application.add_handler(MessageHandler(filters.PHOTO, compress_image))
    application.add_handler(MessageHandler(filters.Document.ALL, pptx_to_pdf))

    print("🤖 Telegram Bot is running...")
    application.run_polling()

# Start Flask and Telegram bot
if __name__ == '__main__':
    from threading import Thread

    # Run Flask in a separate thread
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
    flask_thread.start()

    # Run Telegram bot
    start_telegram_bot()
