from resolver.extensions import db

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.indexable import index_property
from sqlalchemy import text
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property


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

    @hybrid_method
    def get_matches(self, searchterm=None):
        if bool(searchterm):
            # search the identifiers for the term and score them
            matchlist = {}
            for id_name in ["casrn", "preferred_name", "display_name","compound_id"]:
                # an exact match against a top-level identifier
                # yields a 1.0 score
                if self.identifiers[id_name] == searchterm:
                    matchlist[id_name] = 1
            if self.identifiers["synonyms"]:
                synonyms = self.identifiers["synonyms"]
                # a match against a synonym identifier
                # yields whatever the weight of the synonym was
                # set to
                for synonym in synonyms:
                    synid = synonym["identifier"] if synonym["identifier"] else ""
                    if synid == searchterm:
                        matchlist[synonym["synonymtype"]] = synonym["weight"]
            if bool(matchlist):
                return matchlist
            else:
                return None
        else:
            return None

    @hybrid_method
    def score_result(self, searchterm=None):
        matches = self.get_matches(searchterm)
        max_score = 0
        if matches:
            max_key = max(matches, key=matches.get)
            max_score = matches[max_key]
        return max_score


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
