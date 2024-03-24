import os
import sys
import unittest
import click
from flask_migrate import init, migrate, upgrade, downgrade, Migrate
from termcolor import colored
from app import create_app
from app.errors import TillerException

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
        
@app.cli.command("migrate")
def migrate():
    """ Updating Database Schema """
    try:
        """ Initialize the migration environment """
        if not os.path.exists("./migrations"):
            init()
        
        """ Apply the migrations to the database """
        upgrade()
        click.echo(colored(f"db migrations applied successfully ", "green"))
    
    except TillerException as error:
        click.echo(colored(f"error during db migration: {str(error)}", "red"))

@app.cli.command("downgrade")
def downgrade_migrations():
    """ Updating Database Schema """
    try:
        """ undo migrations to the database """
        downgrade()
        click.echo(colored(f"db migrations downgraded successfully ", "green"))
    
    except TillerException as error:
        click.echo(colored(f"error during db migration: {str(error)}", "red"))
        