import os
from dotenv import load_dotenv

"""Default configuration

Use env var to override
"""
import os

load_dotenv("./.flaskenv")
ENV = os.getenv("FLASK_ENV")
DEBUG = ENV == "development"
SECRET_KEY = os.getenv("SECRET_KEY")

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False


class Config(object):

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
    )


JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
