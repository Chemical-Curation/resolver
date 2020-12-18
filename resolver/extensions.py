"""Extensions registry

All extensions here are used as singletons and
initialized in application factory
"""
from flask_sqlalchemy import SQLAlchemy
from indigo import Indigo
from indigo.inchi import IndigoInchi
from passlib.context import CryptContext
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

from resolver.commons.apispec import APISpecExt


db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
migrate = Migrate()
apispec = APISpecExt()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Indigo packages
indigo = Indigo()
indigo_inchi = IndigoInchi(indigo)


def getInchikey(mol: str) -> str:
    """Attempts to convert a string into an inchikey.

    IndigoInchi requires an Indigo molecule to be loaded.
    First load the molecule into indigo then recieve the inchi
    string from IndigoInchi.  Hash that string into the inchikey.
    """
    try:
        loaded_molecule = indigo.loadMolecule(mol)
        inchi = indigo_inchi.getInchi(loaded_molecule)
        return indigo_inchi.getInchiKey(inchi)
    except:
        return mol


def init_db():
    from resolver.config import SQLALCHEMY_DATABASE_URI
    from sqlalchemy import create_engine
    from sqlalchemy_utils import database_exists, create_database

    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    if not database_exists(engine.url):
        create_database(engine.url)
