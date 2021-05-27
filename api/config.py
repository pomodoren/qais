import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

if not os.environ.get("FLASK_ENV") or os.environ.get("FLASK_ENV") == "dev":
    ENV = "dev"
else:
    ENV = "prod"

ENV = 'dev'

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://"
    LOG_TO_STDOUT = os.environ.get("LOG_TO_STDOUT") or True
    LOCAL = os.environ.get("LOCAL") or "localhost:5000"

    SQLALCHEMY_DATABASE_URI =  os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(
        basedir, "database_migrations/" + ENV + ".db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DOCUMENT_PER_PAGE = 25

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
    LOCAL = "localhost:5000"


if not os.environ.get("FLASK_ENV") or os.environ.get("FLASK_ENV") == "dev":
    CONFIG = DevelopmentConfig
else:
    CONFIG = ProductionConfig 