# GovReport Chat Application

GovReport is a chat application designed to help citizens easily report issues to the relevant government agencies. It features a web-based chat interface and a seamless integration with a Telegram bot.

## Features

* **Web Chat Interface**: A clean and intuitive chat interface for users to report issues.
* **Multimedia Support**: Users can send text, images, and audio recordings through the chat.
* **AI-Powered Responses**: The bot uses an AI (Large Language Model) to understand user reports and provide relevant information or next steps.
* **Telegram Integration**: The service is also available as a Telegram chatbot, allowing for easier access and use on the go.
* **Issue Reporting Lifecycle**: The system is designed to help citizens "Recognise" issues, "Report" them easily, and ensure they are "Resolved" by the correct department.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need Python 3.8+ and `pip` installed on your system.

### Installation

1.  **Clone the repository**:
    ```bash
    git clone [repository_url]
    cd [repository_name]
    ```

2.  **Create and activate a virtual environment**:
    It is recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the required packages**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables**:
    The application requires a Telegram API token and potentially other configuration settings for the LLM. Create a `config.py` file in the root directory with the necessary variables.

    ```python
    # config.py
    TELE_API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
    SYSTEM_PROMPT = 'YOUR_LLM_SYSTEM_PROMPT'
    IMAGES_DIR = 'uploads'
    ```

5.  **Create the uploads directory**:
    The application saves uploaded images to a specific folder.
    ```bash
    mkdir uploads
    ```

### Running the Application

Once the prerequisites are met and the environment is set up, you can run the application.

```bash
python app.py