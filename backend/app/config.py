import os
from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass

path = find_dotenv()
load_dotenv(find_dotenv())
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

globals()["SESSION_KEY"] = os.getenv("SESSION_KEY")

@dataclass
class BaseConfig(object):
    SECRET_KEY: str = os.urandom(20)
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    MAIL_PORT: int = os.getenv("MAIL_PORT")
    MAIL_USE_SSL: str = os.getenv("MAIL_USE_SSL")
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    DEBUG: bool = False
    TESTING: bool = False


@dataclass
class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.path.join("sqlite:////" + BASE_DIR, "tiller.sqlite")
    SQLALCHEMY_TRACK_MODIFICATION: bool = False
    SQLALCHEMY_ECHO: bool = False


@dataclass
class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI: str = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATION: bool = False
    SQLALCHEMY_ECHO: bool = False


@dataclass
class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI: str = "sqlite://"
    TESTING: bool = True


config_dict = {
    "development": DevelopmentConfig,
    "default": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
