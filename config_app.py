import os


class ConfigDevelopment:  
    SECRET_KEY = os.getenv("SECRET_KEY", default="TheQuickBrownFoxJumpsOverTheLazyDog")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", default="sqlite:///banking.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  
    DEBUG = True
    TESTING = False
    # SMTP Server Config
    MAIL_SERVER = "smtp"
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = os.getenv("ADMIN_EMAIL", default="example@example.com")
