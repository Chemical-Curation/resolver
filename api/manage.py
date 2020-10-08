import click
from flask.cli import FlaskGroup

from api.app import create_app


def create_api(info):
    return create_app(cli=True)


@click.group(cls=FlaskGroup, create_app=create_api)
def cli():
    """Main entry point"""


@cli.command("init")
def init():
    """Create a new admin user"""
    from api.extensions import db
    from api.models import User

    click.echo("create user")
    user = User(
        username="postgres", email="admin@mail.com", password="postgres", active=True
    )
    db.session.add(user)
    db.session.commit()
    click.echo("created user admin")


if __name__ == "__main__":
    cli()
