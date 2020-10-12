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


@cli.command("load_seed_data")
def load_seed_data():
    from api.models import Substance
    from api.extensions import db

    """Add sample records to the Substance model"""
    # https://chem.nlm.nih.gov/chemidplus/rn/1050-79-9
    s1 = Substance(
        id="DTXCID302000003",
        identifiers="{ 'preferred_name':'Moperone','casrn':'1050-79-9','inchikey': 'AGAHNABIDCTLHW-UHFFFAOYSA-N', 'casalts':[{'casalt':'0001050799','weight':0.5},{'casalt':'1050799','weight':0.5}],'synonyms': [{'synonym': 'Meperon','weight': 0.75},{'synonym': 'Methylperidol','weight': 0.5}]}",
    )
    db.session.add(s1)
    s2 = Substance(
        id="DTXCID302000004",
        identifiers="{ 'preferred_name':'Hydrogen peroxide','casrn':'7722-84-1','inchikey': 'MHAJPDPJQMAIIY-UHFFFAOYSA-N', 'casalts':[{'casalt':'0007722841','weight':0.5},{'casalt':'7722841','weight':0.5}],'synonyms': [{'synonym': 'Hydrogen peroxide [USP]','weight': 0.75},{'synonym': 'Wasserstoffperoxid','weight': 0.5}]}",
    )

    db.session.add(s2)
    db.session.commit()