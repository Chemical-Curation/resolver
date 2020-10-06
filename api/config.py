import os

from dotenv import load_dotenv

load_dotenv("./.env")


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
