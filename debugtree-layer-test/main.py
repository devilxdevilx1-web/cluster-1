# config.py
print("Loading config...")
from database import db_session

def get_config():
    return {"DB": "ACTIVE"}

# database.py
print("Initializing database...")
from user_auth import UserAuth

db_session = "SESSION_OBJ"

# user_auth.py
print("Defining UserAuth...")
from config import get_config

class UserAuth:
    def __init__(self):
        self.config = get_config()

# main.py
try:
    import config
    print("Success!")
except Exception as e:
    print(f"\n[SURFACE ERROR]: {e}")
