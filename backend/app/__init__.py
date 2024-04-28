import os
from flask import Flask
from typing import Optional
from termcolor import colored, cprint
import click
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from flasgger import Swagger
from .swagger import swagger_config, swagger_template
from .errors import *
from .config import config_dict
from .models import db, migrate, User
from .auth import auth_bp
from .views import user_bp
from .utils import mail
from .logger import logger
from dotenv import load_dotenv

load_dotenv()
def create_app(config: Optional[str] = "default") -> None:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_dict[config])
    config_dict[config].init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})
    Swagger(app=app, template=swagger_template, config=swagger_config)

    db.init_app(app=app)
    migrate.init_app(app, db)
    mail.init_app(app=app)

    @app.route("/home")
    def index():
        return "Hello world"

    """ register the blueprints """
    app.add_url_rule("/", endpoint="index")
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)

    """ handle errors """
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(500, handle_500_error)
    app.register_error_handler(403, handle_403_error)
    
    """ handle any other exception """
    @app.errorhandler(HTTPException)
    def handle_exceptions(error):
        response = error.get_response()
        response.data = json.dumps({
            "status code": error.code,
            "name": error.name,
            "description": error.description,
        })
        response.content_type = "application/json"
        return response

    """ ensure instance folders exists """
    try:
        if not os.path.exists(app.instance_path):
            os.mkdir(app.instance_path)
            cprint("Instance path created successfully", "green")
        else:
            pass
    except OSError as error:
        print(colored(f"Error creating the instance: {str(error)}", "red"))

    click.command("say_hello")

    @click.argument("name")
    def hello(name):
        """Say hello to user"""
        print(colored(f"Hello {name}, Server has started successfully at port:{os.getenv('PORT')}", "green"))

    app.cli.add_command(hello("DEV"), name="DEV")

    """ shell context varibables """
    @app.shell_context_processor
    def make_shell_context():
        return {
            "app": app,
            "db": db,
            "user": User,
        }

    """ before any request, the following should be executed """
    @app.before_request
    def create_db():
        with app.app_context():
            db.create_all()
            logger.info(
                colored("Database tables created successfully", "green", attrs=["bold"])
         )
            
    """ use this endpoint for testing purposes """
    @app.route("/palindrome/<string:name>")
    def palindrome(name):
        return name[::-1]
    
    return app
