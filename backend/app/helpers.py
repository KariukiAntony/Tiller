from datetime import datetime, timedelta
from schema import Schema, Optional, Use, And, SchemaError, SchemaMissingKeyError
import re, os
from typing import Union, Optional as OptionalArg
import jwt
from dotenv import load_dotenv, find_dotenv
from termcolor import colored
import redis
from flask import session
from app.config import SESSION_KEY
from app.logger import logger
from app.errors import TillerException

load_dotenv(find_dotenv())
redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=os.getenv("REDIS_PORT", 6379), db=0)

def validate_registration_data(data: dict) -> list:
    """Helper to validate user reg data

    Keyword arguments: user data
    Return: list[bool, response]
    """

    def validate_email(email) -> Union[bool, str]:
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return email.lower()
        else:
            raise SchemaError(f"'{email}' is not a valid email address.")

    valid_schema = Schema(
        {
            "username": And(str, lambda x: x.isalpha() and len(x) > 2),
            Optional("age"): int,
            "email": And(str, Use(validate_email)),
            "password": And(str, lambda x: len(x) > 5),
        }
    )
    try:
        valid_data = valid_schema.validate(data)
        return [True, valid_data]

    except SchemaMissingKeyError as key_error:
        return [False, str(key_error)]
    except SchemaError as schema_error:
        return [False, str(schema_error)]
    except Exception as ex_error:
        return [False, str(ex_error)]


def generate_verify_account_token(data: dict) -> Union[str, bool]:
    try:
        token = jwt.encode(
            data, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM", "HS256")
        )
        return token
    except TillerException as error:
        logger.error(colored(f"an error occured when generating token: {error}", "red"))
        return None


def generate_token(
    data: dict, exp:OptionalArg[bool]=False, duration:OptionalArg[int]=None, refresh:OptionalArg[bool]=False
) -> Union[str, bool]:
    global SESSION_KEY
    try:
        token = None
        if exp and refresh:
            to_encode = data.copy()
            days = (
                int(duration)
                if duration
                else int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES", 1))
            )
            exp = datetime.now() + timedelta(days=days)
            to_encode.update({"exp": exp})
            token = jwt.encode(
                to_encode,
                os.getenv("JWT_SECRET"),
                algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            )
            redis_client.set(data.get("email"), token, ex=timedelta(days=days))

        elif exp and not refresh:
            to_encode = data.copy()
            days = (
                int(duration)
                if duration
                else int(os.environ.get("JWT_TOKEN_EXPIRES", 1))
            )
            exp = datetime.now() + timedelta(days=days)
            to_encode.update({"exp": exp})
            token = jwt.encode(
                to_encode,
                os.getenv("JWT_SECRET"),
                algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            )
            session[SESSION_KEY] = token
        else:
            token = jwt.encode(
                data,
                os.getenv("JWT_SECRET"),
                algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            )
        return token
    except TillerException as error:
        logger.error(colored(f"an error occured when generating token: {error}", "red"))
        return None


def decode_token(token: str) -> Union[dict, bool]:
    try:
        data = jwt.decode(
            token,
            os.environ.get("JWT_SECRET"),
            algorithms=[os.environ.get("JWT_ALGORITHM")],
        )
        return data
    except jwt.DecodeError:
        return False
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False


def validate_login_data(data: dict) -> list:
    """validates the login info passed by the user

    Keyword arguments: login data
    Return: list[bool, str]
    """

    def validate_email(email) -> Union[bool, str]:
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return email.lower()
        else:
            raise SchemaError(f"'{email}' is not a valid email address.")

    valid_schema = Schema(
        {
            "email": And(str, Use(validate_email)),
            "password": And(str, lambda x: len(x) > 5),
        }
    )
    try:
        valid_data = valid_schema.validate(data)
        return [True, valid_data]

    except SchemaMissingKeyError as key_error:
        return [False, str(key_error)]
    except SchemaError as schema_error:
        return [False, str(schema_error)]
    except Exception as ex_error:
        return [False, str(ex_error)]
