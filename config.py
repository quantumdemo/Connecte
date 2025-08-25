import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))  # for local development

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        print("⚠️ DATABASE_URL not found. Falling back to SQLite.")
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False

    # Paystack
    PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
    PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')

    # File uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'profile_pics')

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 8025)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['noreply@connecte.boats']


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False
    PAYSTACK_SECRET_KEY = 'test_secret_key'


config = {
    'deployment': Config,
    'testing': TestingConfig,
    'default': Config
}
