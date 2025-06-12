import os

from dotenv import load_dotenv

load_dotenv("data/.env")

TOKEN = os.getenv("TOKEN")
TRUST_ROLE_ID = os.getenv("TRUST_ROLE_ID")
