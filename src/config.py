
import os
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY=os.getenv('SECRET_KEY')
SESSION_COOKIE_NAME=os.getenv('SESSION_COOKIE_NAME')
CLIENT_ID=os.getenv('CLIENT_ID')
CLIENT_SECRET=os.getenv('CLIENT_SECRET')
TOKIN_INFO=os.getenv('TOKIN_INFO')