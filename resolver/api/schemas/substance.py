import re
from resolver.models import Substance
from resolver.extensions import db
from marshmallow_jsonapi.schema import Schema
from marshmallow_jsonapi import fields
from marshmallow import pre_dump
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
    # the matches will be the fields in which the identifier was found
    matches = fields.Method("score_matches", dump_only=True)
    orm_score = fields.Raw(dump_only=True)

    def score_matches(self, substance, **view_kwargs):
        matches = {}  # a dictionary of matched fields and scores
        if request.args.get("identifier") is not None:
            search_term = request.args.get("identifier")
            id_dict = substance.identifiers
            # start comparing identifiers
            if id_dict["preferred_name"]:
                if re.search(search_term, id_dict["preferred_name"]):
                    matches["preferred_name"] = 1
            if id_dict["display_name"]:
                if re.search(search_term, id_dict["display_name"]):
                    matches["display_name"] = 1
            if id_dict["casrn"]:
                if re.search(search_term, id_dict["casrn"]):
                    matches["casrn"] = 1
            if id_dict["synonyms"]:
                matches["synonyms"] = {}
                for synonym in id_dict["synonyms"]:
                    if re.search(search_term, synonym["identifier"]):
                        matches["synonyms"][synonym["identifier"]] = synonym["weight"]

        return matches

    class Meta:
        type_ = "substance_search_results"
        model = Substance
        sqla_session = db.session
        load_instance = True
