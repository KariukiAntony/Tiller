import functools
from flask import jsonify, request
from typing import Union, Callable
from app.models import User
from app.http_codes import *
from app.helpers import decode_token, session, SESSION_KEY
from app.errors import TillerException

def check_content_type(function:Callable[..., str]) -> Callable[..., Union[str, tuple]]:
    @functools.wraps(function)
    def content_type(*args: list, **kwargs: dict) -> Union[str, tuple]:
        if request.headers.get("content-type") == "application/json":
            return function(*args, **kwargs)
        else:
            return jsonify(
                {"status": "failed", "message": "content-type must be application/json"}
            ), 400
    return content_type


def login_required(function: Callable[..., str]) -> Callable[..., str]:
    @functools.wraps(function)
    def check_if_logged_in(*args: list, **kwargs: dict) -> Union[Callable[..., str], str]:
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
            return jsonify({"status": "failed", "message": str(e)}), HTTP_401_UNAUTHORIZED
    return check_if_logged_in