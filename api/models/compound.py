from api.extensions import db, pwd_context

from flask import jsonify
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.indexable import index_property
from sqlalchemy import text


class Compound(db.Model):
    __tablename__ = "compounds"
    # The identifiers field needs to be indexed for full-JSON search
    # https://www.postgresql.org/docs/9.5/datatype-json.html#JSON-INDEXING
    # https://docs.sqlalchemy.org/en/13/orm/extensions/indexable.html
    __table_args__ = (
        db.Index(
            "ix_sample",
            text("(identifiers->'values') jsonb_path_ops"),
            postgresql_using="gin",
        ),
    )

    id = db.Column(db.String(128), primary_key=True)
    identifiers = db.Column(JSONB)

    def __init__(self, id, identifiers):
        self.id = id
        self.identifiers = identifiers

        casrn = index_property("identifiers", "casrn", default=None)
        preferred_name = index_property("identifiers", "preferred_name", default=None)

    db.Index(
        "ix_identifiers",
        text("(identifiers->'values') jsonb_path_ops"),
        postgresql_using="gin",
    )