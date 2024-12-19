# README: Telegram Bot and Flask API Project

This project is a comprehensive integration of a **Telegram Bot** and a **Flask API**, providing functionalities such as QR code generation, image compression, PowerPoint (PPTX) to PDF conversion, and URL shortening. Below are the details and instructions for setting up and running the project.

## Features

### Flask API Endpoints
1. **QR Code Generation**
   - **Endpoint**: `/generate_qr`
   - **Method**: `POST`
   - **Input**: `link` (URL to encode as QR code)
   - **Output**: PNG image of the QR code

2. **Image Compression**
   - **Endpoint**: `/compress_image`
   - **Method**: `POST`
   - **Input**: Image file
   - **Output**: Compressed image (JPEG format)

3. **PPTX to PDF Conversion**
   - **Endpoint**: `/pptx_to_pdf`
   - **Method**: `POST`
   - **Input**: PPTX file
   - **Output**: Converted PDF file

### Telegram Bot Commands
1. `/start` - Provides a welcome message and feature list.
2. `/help` - Displays available commands and usage instructions.
3. `/view_logs` - Shows recent activity logs (restricted to the bot owner).
4. **Automatic Handling**:
   - Send a link: Generates a QR code.
   - Send an image: Compresses the image.
   - Send a PPTX file: Converts it to PDF.
5. `/shorten <URL>` - Shortens a provided URL using the [shrtco.de API](https://shrtco.de/).

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (obtainable via [BotFather](https://core.telegram.org/bots#botfather))
- SQLite for logging actions
- Microsoft PowerPoint installed (for PPTX to PDF conversion on Windows)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <https://github.com/abhinai2244/qr-code-generator-bot.git>
   cd <repository-folder>
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Bot Token and Owner Information**:
   - Open the script and replace `TOKEN` with your Telegram Bot Token.
   - Replace `OWNER_USERNAME` and `OWNER_USER_ID` with the bot owner's details.

4. **Set Up SQLite Database**:
   The script automatically creates a `logs.db` file and the necessary `logs` table.

## Running the Project

1. **Start Flask API**:
   ```bash
   python <script_name>.py
   ```
   The Flask API will run on `http://0.0.0.0:5000/`.

2. **Start Telegram Bot**:
   The Telegram bot starts automatically in a separate thread when the script runs.

## Usage Instructions

- Use the Telegram Bot to send links, images, PPTX files, or commands as per the feature list.
- Use the Flask API for programmatic access to QR code generation, image compression, and file conversion services.

## Technical Notes

1. **Dependencies**:
   - `Flask` for API endpoints
   - `python-telegram-bot` for Telegram Bot functionality
   - `qrcode` for QR code generation
   - `Pillow` for image handling
   - `win32com.client` for PPTX to PDF conversion using PowerPoint

2. **Error Logging**:
   - Errors during PPTX to PDF conversion or other operations are logged and notified to the bot owner via Telegram.

3. **Security**:
   - Ensure the bot token is kept secret.
   - Use secure endpoints if exposing the Flask API publicly.

## Troubleshooting

- **PowerPoint Errors**:
  Ensure that Microsoft PowerPoint is installed and properly configured.
- **Telegram Bot Not Responding**:
  Verify the bot token and check network connectivity.
- **SQLite Errors**:
  Ensure the `logs.db` file is writable and not corrupted.

## License
This project is licensed under the MIT License.

## Contributions
Feel free to submit issues or pull requests for improvements or additional features.

---

Happy coding! 🚀

