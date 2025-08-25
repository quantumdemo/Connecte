import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # Database configuration
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        # Try to build PostgreSQL URI from Railway variables
        pg_user = os.environ.get("PGUSER")
        pg_pass = os.environ.get("PGPASSWORD")
        pg_host = os.environ.get("PGHOST")
        pg_port = os.environ.get("PGPORT")
        pg_db   = os.environ.get("PGDATABASE")

        if all([pg_user, pg_pass, pg_host, pg_port, pg_db]):
            SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
            )
        else:
            # Railway environment exists but vars not linked → fallback
            print("⚠️ WARNING: Railway Postgres variables not found. Using SQLite instead.")
            SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
    else:
        # Local development fallback
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False

    # Paystack
    PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
    PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')

    # File uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'profile_pics')

    # Email configuration
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
    'development': Config,
    'testing': TestingConfig,
    'default': Config
}
