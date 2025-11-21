import click
from flask.cli import with_appcontext
from .commands import init_db, seed_data

def register_commands(app):
    """注册CLI命令"""
    app.cli.add_command(init_db)
    app.cli.add_command(seed_data)