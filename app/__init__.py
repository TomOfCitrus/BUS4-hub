from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

from app import routes, models

def create_app():
    return app