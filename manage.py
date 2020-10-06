from flask.cli import FlaskGroup
from api import app, db, Compound

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("load_seed_data")
def load_seed_data():
    # https://chem.nlm.nih.gov/chemidplus/rn/1050-79-9
    c1 = Compound(
        id="DTXCID302000003",
        identifiers='{ "preferred_name":"Moperone","casrn":"1050-79-9","inchikey": "AGAHNABIDCTLHW-UHFFFAOYSA-N", "casalts":[{"casalt":"0001050799","weight:0.5},{"casalt":"1050799","weight":0.5}],"synonyms": [{"synonym": "Meperon","weight": 0.75},{"synonym": "Methylperidol","weight": 0.5}]}',
    )
    db.session.add(c1)
    db.session.commit()


if __name__ == "__main__":
    cli()