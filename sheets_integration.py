import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def init_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    return client

def log_expense(telegram_id, name, amount, purpose, date_time):
    client = init_sheets()
    sheet = client.open('Finanses').sheet1  # Replace with your Google Sheet name
    row = [telegram_id, name, amount, purpose, date_time]
    sheet.append_row(row)

# Example usage in a test script
# if __name__ == "__main__":
#     telegram_id = "000000"
#     name = "Testetājs"
#     amount = 2.50
#     purpose = "Pārbaudīt integrāciju"
#     date_time = datetime.now().strftime("%d.%m.%Y %H")
#
#     log_expense(telegram_id, name, amount, purpose, date_time)