import json

ACCOUNTS_FILE = 'tg_accounts.json'

def load_accounts():
    with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as file:
        json.dump(accounts, file, ensure_ascii=False, indent=4)

def get_unregistered_names():
    accounts = load_accounts()
    return [account['name'] for account in accounts if account['telegram_id'] == 'Not Registered']

def get_registered_names():
    accounts = load_accounts()
    return [account['name'] for account in accounts if account['telegram_id'] != 'Not Registered']

def register_account(name, telegram_id):
    accounts = load_accounts()
    for account in accounts:
        if account['name'] == name:
            account['telegram_id'] = telegram_id
            save_accounts(accounts)
            return True
    return False