from resolver.models import Substance
from resolver.extensions import db, getInchikey
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
    # the matches will be the fields in which the identifier was found
    matches = fields.Function(
        lambda obj: obj.get_matches(getInchikey(request.args.get("identifier")))
    )
    score = fields.Function(
        lambda obj: obj.score_result(getInchikey(request.args.get("identifier")))
    )

    class Meta:
        type_ = "substance_search_results"
        self_view_many = "resolved_substance_list"
        model = Substance
        sqla_session = db.session
        load_instance = True
