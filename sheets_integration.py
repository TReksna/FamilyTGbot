import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
import json

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

# Google Drive setup
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'credentials.json'
FOLDER_ID = '1N1aBdWH-4E3hcQxmIWaq669v4DRN31aq'  # Replace with your Google Drive folder ID

def initialize_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=DRIVE_SCOPES)
    service = build('drive', 'v3', credentials=creds)
    return service

def upload_file_to_drive(file_path, file_name):
    if not file_path or not file_name:
        raise ValueError("file_path and file_name must be provided")
    service = initialize_drive_service()
    file_metadata = {
        'name': file_name,
        'parents': [FOLDER_ID]
    }
    media = MediaFileUpload(file_path, mimetype='image/jpeg')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

def get_checkin_questions():
    client = init_sheets()
    sheet = client.open('Check in questions').sheet1
    return sheet.get_all_records()

def log_checkin_response(user_name, date, question, rating, followup):
    client = init_sheets()
    sheet = client.open(user_name).sheet1
    row = [date, question, rating, followup]
    sheet.append_row(row)

def get_recent_questions(user_name, days=2):
    client = init_sheets()
    sheet = client.open(user_name).sheet1
    records = sheet.get_all_records()
    if days > 0:
        recent_questions = [record['Question'] for record in records if (datetime.now() - datetime.strptime(record['Date'], '%d.%m.%Y')).days <= days]
    else:
        recent_questions = [record['Question'] for record in records]  # Get all questions if days is 0
    return recent_questions

def load_accounts():
    with open('tg_accounts.json', 'r', encoding='utf-8') as file:
        accounts = json.load(file)
    return {account['telegram_id']: account['name'] for account in accounts if account['telegram_id'] != 'Not Registered'}




# Example usage in a test script
# if __name__ == "__main__":
#     telegram_id = "000000"
#     name = "Testetājs"
#     amount = 2.50
#     purpose = "Pārbaudīt integrāciju"
#     date_time = datetime.now().strftime("%d.%m.%Y %H")
#
#     log_expense(telegram_id, name, amount, purpose, date_time)
#
#     file_path = 'path_to_your_image.jpg'
#     file_name = 'uploaded_image.jpg'
#     file_id = upload_file_to_drive(file_path, file_name)
#     print(f'File ID: {file_id}')
