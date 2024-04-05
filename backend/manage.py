import os
import sys
import unittest
import click
from flask_migrate import init, upgrade, downgrade
from termcolor import colored
from shutil import move, copymode
from tempfile import mkstemp
from pyngrok import ngrok
from app import create_app
from app.errors import TillerException

""" CONSTANTS """
BASE_PATH = os.path.abspath(os.path.dirname(__name__))
ENV_PATH = os.path.join(BASE_PATH, ".env")
PORT = os.getenv("PORT", 5000)

config = os.environ.get("CONFIG") or "default"
app = create_app(config)


@app.cli.command()
def hello():
    click.echo("Hello, Welcome to Tiller; your smart note taker. ")


@app.cli.command()
def tests():
    text = """
    -----------------------------------------------
    Running Tiller Tests. Please wait for a while.
    --------------------------------------------
    """
    click.echo(colored(text, "green"))
    loader = unittest.TestLoader()
    loader.testMethodPrefix = "test_"
    tests = loader.discover("./app", pattern="test*.py")
    results = unittest.TextTestRunner(verbosity=2).run(tests)
    if not results.wasSuccessful():
        print(colored("\n----Failed to run all the tests....", "red"))
        sys.exit(1)
    else:
        print(colored("All tests run successfully", "blue"))


@app.cli.command("migrate")
def migrate():
    """Updating Database Schema"""
    try:
        """Initialize the migration environment"""
        if not os.path.exists("./migrations"):
            init()

        """ Apply the migrations to the database """
        upgrade()
        click.echo(colored(f"db migrations applied successfully ", "green"))

    except TillerException as error:
        click.echo(colored(f"error during db migration: {str(error)}", "red"))


@app.cli.command("downgrade")
def downgrade_migrations():
    """Updating Database Schema"""
    try:
        """undo migrations to the database"""
        downgrade()
        click.echo(colored(f"db migrations downgraded successfully ", "green"))

    except TillerException as error:
        click.echo(colored(f"error during db migration: {str(error)}", "red"))


@app.cli.command()
def tunnel():
    """expose the app using ngrok ..."""

    def update_env(file_path: str, initial: str, final: str) -> None:

        file_desc, temp_file_path = mkstemp()
        with os.fdopen(file_desc, "w") as new_file:
            with open(file_path, "r") as old_file:
                lines = [line.strip() for line in old_file if line.strip()]
                for line in old_file:
                    new_file.write(line.replace(initial, final))

        copymode(file_path, temp_file_path)
        os.remove(file_path)
        move(temp_file_path, file_path)  # rename the tempfile as .env

    try:
        """update env urls"""
        print(colored("[+] updating env variables ...", "green"))
        http_tunnel = ngrok.connect(PORT, "http", "Tiller tunnel")
        print("base url: {0}".format(http_tunnel.public_url))

        urls = dict(
            FRONTEND_URL={
                "initial": 'FRONTEND_URL = ""',
                "final": f"FRONTEND_URL = {http_tunnel.public_url}/api/v1/auth/",
            },
            NGROK_URL={
                "initial": 'NGROK_URL = ""',
                "final": f"NGROK_URL = {http_tunnel.public_url}",
            },
        )

        for url, item in urls.items():
            update_env(ENV_PATH, item.get("initial"), item.get("final"))
            print(f"{url} full url: {item.get('final')}")

        print(
            colored(
                "[+] updated the env variables fully. Starting the flask app..", "blue"
            )
        )
        # start the flask application
        os.system("flask run ")
        ngrok_proccess = ngrok.get_ngrok_process()
        ngrok_proccess.proc.wait()

    except KeyboardInterrupt:
        print(colored("[-] stopping the server ....", "green"))
        tunnels = ngrok.get_tunnels()
        map(lambda tunnel: ngrok.disconnect(tunnel.public_url), tunnels)

        """ return env file to its original state """
        [
            update_env(ENV_PATH, item.get("final"), item.get("initial"))
            for _, item in urls.items()
        ]
        print(colored(f"[+] successfully retained env file..", "green"))
        ngrok.kill()

    except TillerException as error:
        print(colored(f"[x] an error has occured..: {str(error)}", "red"))
        sys.exit(1)
