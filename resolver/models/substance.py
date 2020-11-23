from resolver.extensions import db

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.indexable import index_property
from sqlalchemy import text
from sqlalchemy.sql import func, literal
from sqlalchemy.orm import query_expression


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
    identifiers = db.Column(JSONB, nullable=False)

    casrn = index_property("identifiers", "casrn", default=None)
    preferred_name = index_property("identifiers", "preferred_name", default=None)
    orm_score = query_expression()


ix_identifiers = db.Index(
    "ix_identifiers",
    Substance.identifiers,
    text("(identifiers->'values') jsonb_path_ops"),
    postgresql_using="gin",
)
ix_identifiers_tsv = db.Index(
    "ix_identifiers_tsv",
    Substance.identifiers,
    func.to_tsvector("english", Substance.identifiers),
    postgresql_using="gin",
)

if __name__ == "__main__":
    ix_identifiers.create(bind=db.engine)
    ix_identifiers_tsv.create(bind=db.engine)
