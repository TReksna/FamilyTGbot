# FamilyTGbot

FamilyTGbot is a Telegram bot designed to assist with various family activities such as managing expenses and registering user accounts. The bot uses the `python-telegram-bot` library for Telegram interactions and integrates with Google Sheets for data storage.

## Features

- **User Registration**: Register users with their Telegram IDs.
- **Expense Logging**: Log family expenses with details such as the payer, amount, and purpose.

## Project Structure

The project is organized into several modules for easier management:

- **main.py**: The main entry point of the bot. It configures the application and sets up the command handlers.
- **registration.py**: Handles user registration functionality.
- **finances.py**: Handles expense logging functionality.
- **accounts_manager.py**: Manages interactions with the `tg_accounts.json` file.
- **sheets_integration.py**: Manages Google Sheets integration.
- **messages.json**: Contains all the text messages and media paths used by the bot.

## Setup

### Prerequisites

- Python 3.7 or higher
- Pip (Python package installer)
- A Google Cloud project with Sheets and Drive APIs enabled
- A Telegram bot token

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/TReksna/FamilyTGbot.git
   cd FamilyTGbot
