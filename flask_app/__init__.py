from flask import Flask
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("secret_key")

bcrypt = Bcrypt(app)

DB = os.environ.get("db_name")