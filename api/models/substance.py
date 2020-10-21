from api.extensions import db, pwd_context

from flask import jsonify
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.indexable import index_property
from sqlalchemy import text
from sqlalchemy.sql import func


class Substance(db.Model):
    """
    Indexed Substance

    The identifiers field is a JSONB object with keys that may change to meet
    different user requirements.
    The JSON keys can be individually queried in PostgreSQL like this:
    SELECT id, identifiers->>'preferred_name' as preferred_name FROM substances

    """

    __tablename__ = "substances"
    # The identifiers field needs to be indexed for full-JSON search
    # https://www.postgresql.org/docs/9.5/datatype-json.html#JSON-INDEXING
    # https://docs.sqlalchemy.org/en/13/orm/extensions/indexable.html

    id = db.Column(db.String(128), primary_key=True)
    identifiers = db.Column(JSONB)
    __table_args__ = (
        db.Index(
            "ix_sample",
            text("(identifiers->'values') jsonb_path_ops"),
            postgresql_using="gin",
        ),
        db.Index(
            "ix_substances_tsv",
            func.to_tsvector("english", identifiers),
            postgresql_using="gin",
        ),
    )

    # def __init__(self, id, identifiers):
    #     self.id = id
    #     self.identifiers = identifiers
    #
    #     casrn = index_property("identifiers", "casrn", default=None)
    #     preferred_name = index_property("identifiers", "preferred_name", default=None)
