from flask import Flask
from db.connector import get_user
app = Flask(__name__)
@app.route('/user')
def user(): return get_user(1)