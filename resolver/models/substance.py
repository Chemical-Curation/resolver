from resolver.commons.search_helpers import prep_casrn
from resolver.extensions import db

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.indexable import index_property
from sqlalchemy import text
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_method


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
            for key, value in self.identifiers.items():
                # an exact match against a top-level identifier
                # yields a 1.0 score
                if type(value) == str:
                    # exact match
                    if value.casefold() == searchterm.casefold():
                        matchlist[key] = 1
                    # corrected match
                    else:
                        score = self.search_corrections(value, searchterm, [prep_casrn])
                        if score:
                            matchlist[key] = score

                # Matches against lists of dicts will compared by their "identifier"
                # and be scored with their custom score "weight"
                if type(value) == list:
                    for entry in value:
                        # fetch the identifier for the list entry.
                        identifier = entry.get("identifier", None)
                        if identifier.casefold() == searchterm.casefold():
                            # TODO: one to many relationships are currently a list of objects
                            #     that contain the keys:
                            #         - "identifier" (key to match on)
                            #         - "weight" (score) and
                            #         - "synonymtype" (the reason for this match on the match list)
                            #     It may make more sense to replace "synonymtype" with something
                            #     more generic like "match_name" to avoid implementation specific
                            #     terminology.
                            matchlist[entry["synonymtype"]] = entry["weight"]

            if bool(matchlist):
                return matchlist
            else:
                return None
        else:
            return None

    def search_corrections(self, value, searchterm, cleaners):
        for cleaning_func in cleaners:
            cleaned_string = cleaning_func(searchterm)
            if value == cleaned_string:
                return 0.75  # primary match of 1 - .25 penalty for mistype

    @hybrid_method
    def score_result(self, searchterm=None):
        """
        Technical debt here: the identifiers in the indexed document are hard-coded
        into the scoring loop
        https://github.com/Chemical-Curation/resolver/pull/16#discussion_r536216962
        """
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
