import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SECRET_KEY = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, "database")
    os.makedirs(SQLITE_DB_DIR, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "project_db.sqlite3")
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
    SECRET_KEY = "Abhi_key"
    DEBUG = True
