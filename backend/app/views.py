from flask import Blueprint, jsonify, request
from .helpers import *
from .decorators import *

user_bp = Blueprint("user_bp", __name__, url_prefix="/api/v1/user")


@user_bp.route("/profile", methods=["GET", "PATCH"])
@login_required
def update_profile(user):
    if request.method == "PATCH":
        data = request.get_json()
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                continue
        user.update()
        return user.to_json(), HTTP_202_ACCEPTED
    
    elif request.method == "GET":
        return user.to_json()
    
    else:
        pass

