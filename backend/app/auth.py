import json
from flask import Blueprint, jsonify, redirect, request, session
from flasgger import swag_from
from app.http_codes import *
from .helpers import (
    validate_registration_data,
    validate_login_data,
    generate_verify_account_token,
    generate_token,
    decode_token,
    SESSION_KEY,
)
from .decorators import check_content_type, login_required
from .models import User, colored, os, db
from .utils import send_mail, TillerException

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/v1/auth")


@auth_bp.route("/signup", methods=["POST"])
@swag_from("./docs/auth/signup.yaml")
@check_content_type
def signup():
    data = request.get_json()
    status, resp = validate_registration_data(data)
    if status == True:
        if not User.get_user_by_email(data["email"]):
            User(**resp)
            payload = {"email": data.get("email")}
            token = generate_verify_account_token(payload)
            redirect_url = f"{request.url_root}api/v1/auth/verifyaccount?token={token}"
            email_message = {
                "sender": os.getenv("MAIL_USERNAME"),
                "recipients": data.get("email"),
                "subject": "Account Verification",
                "body": f'Hello {data.get("username")},'
                + "\nThank you for registering with Tiller\n"
                + "\nClick this link to verify your email\n"
                + "\n "
                + redirect_url,
            }
            resp = send_mail(email_message)
            if resp:
                print(colored("Email sent successfully", "green"))
            return (
                jsonify(
                    {"status": "success", "message": "account created successfully"}
                ),
                HTTP_201_CREATED,
            )
        else:
            return (
                jsonify(
                    {"status": "Failed", "message": "user with account already exists"}
                ),
                HTTP_409_CONFLICT,
            )
    else:
        return jsonify({"status": "Failed", "messge": resp}), HTTP_400_BAD_REQUEST


@auth_bp.route("/verify-account")
def verify_account():
    token = request.args.get("token")
    if token:
        data = decode_token(token)
        if data:
            user = User.get_user_by_email(data.get("email"))
            user.verified = True
            db.session.commit()
            return redirect(
                os.getenv("FRONTEND_URL", " ") + "login?message=success", code=200
            )
        else:
            return jsonify({"error": "invalid verification url"}), HTTP_400_BAD_REQUEST
    else:
        return jsonify({"error": "Invalid verification url"}), HTTP_400_BAD_REQUEST


@auth_bp.route("/login", methods=["POST"])
@swag_from("./docs/auth/login.yaml")
def login():
    data = request.get_json()
    status, response = validate_login_data(data)
    if status:
        if User.login_user(response):
            return (
                jsonify(
                    {
                        "status": "success",
                        "access_token": generate_token(
                            {"email": response.get("email")}, True
                        ),
                        "refresh_token": generate_token(
                            {"email": response.get("email")}, exp=True, refresh=True
                        ),
                    }
                ),
                HTTP_200_OK,
            )
        else:
            return make_response(
                "failed", "invalid email or password", HTTP_401_UNAUTHORIZED
            )
    else:
        return make_response("failed", response, HTTP_400_BAD_REQUEST)


@auth_bp.route("/forgot-password", methods=["POST"])
@swag_from("./docs/auth/forgot-pass.yaml")
def forgot_password():
    email = request.get_json().get("email")
    if email:
        if User.get_user_by_email(email.lower()):
            token = generate_token(
                {
                    "email": email,
                },
                True,
                duration=1,
            )
            redirect_url = f"{request.url_root}api/v1/auth/password-reset?token={token}"
            email_message = {
                "subject": "Password Change",
                "sender": os.getenv("MAIL_USERNAME"),
                "recipients": email,
                "body": f"Hello !\n"
                + "Click the link below and follow the instructions to reset your password\n"
                + redirect_url,
            }
            resp = send_mail(email_message)
            if resp:
                print(colored("Email sent successfully", "green"))
            return make_response(
                "success", "reset password link sent to your email", HTTP_200_OK
            )
        else:
            return make_response(
                "error", f"user with email: {email} not found", HTTP_404_NOT_FOUND
            )

    else:
        return make_response("error", "email is required", HTTP_400_BAD_REQUEST)


@auth_bp.route("/password-reset", methods=["GET"])
def check_reset_token():
    token = request.args.get("token")
    if token:
        data = decode_token(token)
        if data:
            print(data)
            return redirect(
                f'{os.getenv("FRONTEND_URL", " ")}/password-reset?auth_token={token}',
                code=302,
            )
        else:
            return make_response("error", "invalid url", HTTP_400_BAD_REQUEST)
    else:

        return make_response("error", "invalid url", HTTP_400_BAD_REQUEST)


@auth_bp.route("/password-reset", methods=["POST"])
@swag_from("./docs/auth/password-reset.yaml")
def password_reset():
    token = request.get_json().get("token")
    decoded_data = decode_token(token)
    if decoded_data:
        user = User.get_user_by_email(decoded_data.get("email"))
        password = request.get_json().get("password")
        if len(password) > 5:
            user.password = password
            user.update()
            return make_response(
                "success", "password reset successfully", HTTP_202_ACCEPTED
            )
        else:
            return make_response("error", "password too short", HTTP_400_BAD_REQUEST)
    return make_response("error", "invalid token", HTTP_401_UNAUTHORIZED)


@auth_bp.route("/logout")
@swag_from("./docs/auth/logout.yaml")
@login_required
def logout(user):
    try:
        session.pop(SESSION_KEY)
        return make_response("success", "user logged out successfully", HTTP_200_OK)
    except TillerException as e:
        return make_response(
            "error", "error when logging out the user", HTTP_500_INTERNAL_SERVER_ERROR
        )


def make_response(status: str, message: str, status_code: int) -> str:
    return (
        jsonify(
            {
                "status": status,
                "message": message,
            }
        ),
        status_code,
    )
