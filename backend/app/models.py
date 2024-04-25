import os
from sqlalchemy import exc
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from termcolor import colored
from typing import Optional, final, Union
from datetime import datetime
from hashlib import md5
from dataclasses import dataclass

# local imports
from app.errors import TillerException
from .logger import logger
from .utils import hash_pwd, verify_password

db = SQLAlchemy()
migrate = Migrate()

# CONSTANTS
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
PER_PAGE = 5
PAGE = 1


class Helper(object):
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        try:
            db.session.commit()
            return True
        except exc.IntegrityError as e:
            db.session.rollback()
            logger.error(colored(f"Error updating: {str(e)}", "red"))
            return False


@final
class User(db.Model, Helper):
    __tablename__ = "user"
    id = db.Column(db.Integer(), primary_key=True, index=True, unique=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(500), nullable=False, unique=True)
    _password = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(500), default=lambda: User.generate_image_avatar())
    verified = db.Column(db.Boolean(), default=False)
    date_created = db.Column(
        db.DateTime(), onupdate=datetime.now().replace(second=0, microsecond=0)
    )
    date_updated = db.Column(
        db.DateTime(), default=datetime.now().replace(second=0, microsecond=0)
    )
    notes = db.relationship("Note", backref=db.backref("user", lazy="joined"), passive_deletes=True, lazy="dynamic")

    def __init__(self, *args: list, **kwargs: dict) -> None:
        self.username = kwargs.get("username", "anonymous")
        self.email = kwargs.get("email")
        self.password = kwargs.get("password")
        self.image = self.generate_image_avatar()
        if kwargs.get("date_updated") is not None:
            self.date_updated = datetime.now().strftime(TIMESTAMP_FORMAT)
        else:
            self.date_updated = self.get_datetime()
        self.save_to_db()

    @property
    def password(self) -> bytes:
        return self._password

    @password.setter
    def password(self, password) -> bytes:
        if len(password) > 5 and type(password) == str:
            self._password = hash_pwd(password)
        else:
            raise TillerException("Invalid password")

    def get_datetime(self):
        return datetime.now().replace(second=0, microsecond=0)

    def generate_image_avatar(self, size: Optional[int] = 80) -> str:
        """Generates an image for the user using the gravatar api"""
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        url = f"https://www.gravatar.com/avatar/{digest}?d=retro&s={size}"
        return url

    @classmethod
    def get_user(cls, id):
        """get the user according to id passed"""
        user = cls.query.filter_by(id=int(id)).first()
        if user:
            return user
        else:
            return False

    @classmethod
    def get_user_by_email(cls, email) -> Union[object, bool]:
        """get the user according email passed"""
        user = cls.query.filter_by(email=email).first()
        if user:
            return user
        else:
            return False

    @classmethod
    def login_user(cls, data: dict) -> bool:
        user = cls.get_user_by_email(data.get("email"))
        if user:
            return verify_password(data.get("password"), user.password)
        return False

    def to_json(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "image": self.image,
            "date_created": self.date_created,
        }

    def __eq__(self, __value: object) -> bool:
        return self.id == __value.id and self.email == __value.email

    def __str__(self):
        return f"<Username: {self.username}>"


@dataclass(init=False)
class Note(db.Model, Helper):
    __tablename__ = "note"
    id = db.Column(db.Integer(), primary_key=True, index=True)
    transcript = db.Column(db.Text(), nullable=False)
    summary = db.Column(db.Text(), nullable=False)
    audio_url = db.Column(db.String(5000), unique=True, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id",  ondelete="CASCADE"), nullable=False)
    date_created = db.Column(
        db.DateTime(), default=datetime.now().replace(second=0, microsecond=0)
    )

    def __init__(self, *args: list, **kwargs: dict) -> None:
        self.transcript = kwargs.get("transcript")
        self.summary = kwargs.get("summary")
        self.audio_url = kwargs.get("audio_url")
        self.user_id = kwargs.get("user_id")
        # add data to db
        self.save_to_db()
        
    @classmethod()
    def paginate(cls, page: Optional[int]=PAGE, per_page: Optional[int]=PER_PAGE):
        return cls.query.order_by(Note.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    @classmethod
    def get_by_id(cls, id:int):
        return cls.query.filter_by(id=id).first_or_404()
    
        
    def to_json(self):
        return {
            "transcript": self.transcript,
            "summary": self.summary,
            "audio_url": self.audio_url,
            "date_created": self.date_created
        }
        
    def __str__(self) -> str:
        return "<note id: {0}>".format(self.id)