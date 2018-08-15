import os

from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv(dotenv_path='.env')

GITHUB_SECRET = os.environ.get('GITHUB_SECRET')
SERVER_URL = os.environ.get('SERVER_URL')
TELEGRAM_ID = os.environ.get('TELEGRAM_ID')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
