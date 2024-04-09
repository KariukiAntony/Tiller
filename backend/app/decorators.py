import functools
import os
from flask import jsonify, request
from typing import Union, Callable
from cachelib.redis import RedisCache
from cachelib.simple import SimpleCache
from termcolor import colored
from app.models import User
from app.http_codes import *
from app.helpers import decode_token, session, SESSION_KEY
from app.errors import TillerException

""" CONTANTS """
HOST = os.environ.get("REDIS_HOST", "localhost")
PORT = os.environ.get("REDIS_PORT")
PASSWORD = os.environ.get("REDIS_PASSWORD", None)
DEFAULT_TIMEOUT = os.environ.get("CACHE_DEFAULT_TIMEOUT", 300)
config = os.environ.get("CONFIG") or "default"


def connect_redis_locally() -> RedisCache:
    return RedisCache(
        host=HOST,
        port=int(PORT),
        default_timeout=DEFAULT_TIMEOUT,
        key_prefix="tiller/%s",
    )


def cache_production() -> RedisCache:
    return SimpleCache(default_timeout=int(DEFAULT_TIMEOUT))


def check_content_type(
    function: Callable[..., str]
) -> Callable[..., Union[str, tuple]]:
    @functools.wraps(function)
    def content_type(*args: list, **kwargs: dict) -> Union[str, tuple]:
        if request.headers.get("content-type") == "application/json":
            return function(*args, **kwargs)
        else:
            return (
                jsonify(
                    {
                        "status": "failed",
                        "message": "content-type must be application/json",
                    }
                ),
                400,
            )

    return content_type


def login_required(function: Callable[..., str]) -> Callable[..., str]:
    @functools.wraps(function)
    def check_if_logged_in(
        *args: list, **kwargs: dict
    ) -> Union[Callable[..., str], str]:
        try:
            auth_token = request.headers.get("Authorization")
            if auth_token and len(auth_token.split(" ")) > 1:
                token = auth_token.split(" ")[1]
                if token and session.get(SESSION_KEY) == token:
                    decoded_dict = decode_token(token)
                    if decoded_dict:
                        user = User.get_user_by_email(decoded_dict.get("email"))
                        return function(user, *args, **kwargs)
                    else:
                        raise TillerException("Invalid Authorization token")
                else:
                    raise TillerException("Invalid Authorization token")
            else:
                raise TillerException("Auth Token required")

        except TillerException as e:
            return (
                jsonify({"status": "failed", "message": str(e)}),
                HTTP_401_UNAUTHORIZED,
            )

    return check_if_logged_in


def cache_response(timeout: int = 300):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args: list, **kwargs: dict):
            cache = cache_production() if config == "production" else connect_redis_locally()
            cached_key = request.url
            cached_value = cache.get(cached_key)
            if cached_value is not None:
                return cached_value
            else:
                to_cache = function(*args, **kwargs)
                print(colored(f"[++] value to cache: {cached_value}", "green"))
                cache.set(cached_key, to_cache, timeout=timeout)
                return to_cache

        return wrapper

    return decorator
