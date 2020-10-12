from api.models import Substance
from api.extensions import ma, db
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields


class SubstanceSchema(Schema):

    id = ma.Str(required=True)
    identifiers = ma.Dict(required=True)

    class Meta:
        type_ = "substances"
        model = Substance
        sqla_session = db.session
        load_instance = True


# TODO: create a new schema for results. It needs to contain all
# the scoring metadata


class SubstanceSearchResultSchema(Schema):

    id = ma.Str(required=True)
    identifiers = ma.Dict(required=True)
    # the matches will be the fields in which the identifier was found
    matches = fields.Function(
        lambda obj: "[{}, {}]".format("matching field 1", "matching field 2")
    )
    # the score will be calculated in the resolver method
    score = fields.Function(lambda obj: 1)

    class Meta:
        type_ = "substance_rearch_results"
        model = Substance
        sqla_session = db.session
        load_instance = True