import re
from resolver.models import Substance
from resolver.extensions import db
from marshmallow_jsonapi.schema import Schema
from marshmallow_jsonapi import fields
from flask import request


class SubstanceSchema(Schema):
    id = fields.Str()
    identifiers = fields.Dict()  # Swagger does not render this if it's Raw

    class Meta:
        model = Substance
        type_ = "substance"
        self_view = "substance_detail"
        self_view_kwargs = {"id": "<id>"}
        self_view_many = "substance_list"


class SubstanceSearchResultSchema(Schema):

    id = fields.Str(required=True)
    identifiers = fields.Raw(required=True)

    # the net score is the highest of all the match scores,
    # with some tiebreaking logic TBD
    searchscore = fields.Method("rollup_matches", dump_only=True)

    def rollup_matches(self, substance, **view_kwargs):
        matches = {}  # a dictionary of matched fields and scores
        match_summary = {}

        if request.args.get("identifier") is not None:
            # append regex characters to force full-string matching for now
            search_term = f"^{request.args.get('identifier')}$"

            id_dict = substance.identifiers
            # start comparing identifiers
            if id_dict["preferred_name"]:
                if re.search(search_term, id_dict["preferred_name"]):
                    matches["Matched preferred_name"] = 1
            if id_dict["display_name"]:
                if re.search(search_term, id_dict["display_name"]):
                    matches["Matched display_name"] = 1
            if id_dict["casrn"]:
                if re.search(search_term, id_dict["casrn"]):
                    matches["Matched casrn"] = 1

            if id_dict["synonyms"]:
                for synonym in id_dict["synonyms"]:
                    if re.search(search_term, synonym["identifier"]):
                        matches[f'Matched synonym {synonym["identifier"]}'] = synonym[
                            "weight"
                        ]

            if bool(matches):
                max_key = max(matches, key=matches.get)
                max_score = matches[max_key]
                match_summary = {max_key: max_score}

        return match_summary if bool(match_summary) else None

    class Meta:
        type_ = "substance_search_results"
        model = Substance
        sqla_session = db.session
        load_instance = True
        ordered = True
