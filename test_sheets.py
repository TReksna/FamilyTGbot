from sheets_integration import log_expense
from datetime import datetime

def test_log_expense():
    telegram_id = "000000"
    name = "Testetājs"
    amount = 2.50
    purpose = "Pārbaudīt integrāciju"
    date_time = datetime.now().strftime("%d.%m.%Y %H")

    log_expense(telegram_id, name, amount, purpose, date_time)
    print("Test log expense executed successfully.")

if __name__ == "__main__":
    test_log_expense()