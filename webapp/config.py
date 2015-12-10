from os.path import join, dirname
from dotenv import load_dotenv
from os import environ
from sqlalchemy.engine.url import URL

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class Config(object):
    DEBUG = False
    CSRF_ENABLED = True
    SECRET_KEY = 'change_this'

    DATABASE = {
        'drivername' : 'postgres',
        'host' : environ["DB_HOST"],
        'port' : environ["DB_PORT"],
        'username' : environ["DB_USERNAME"],
        'password' : environ["DB_PASSWORD"],
        'database' : environ["DB_DATABASE"],
    }

    SQL_ALCHEMY_DATABASE_URI = URL(**DATABASE)


class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
