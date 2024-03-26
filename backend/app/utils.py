import bcrypt
from flask_mail import Mail, Message

mail = Mail()
from app.errors import TillerException
def hash_pwd(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def send_mail(data) -> bool:
    try:
        mail_message = Message(
        data.get("subject"),
        sender = data.get("sender"), 
        recipients = [data.get("recipients")])
        mail_message.body = data.get("body")
        mail.send(mail_message)
        return True
    except TillerException as e:
        return False
    