from api.models import Compound
from api.extensions import ma, db
from marshmallow_jsonapi.flask import Schema


class CompoundSchema(Schema):

    id = ma.Str(required=True)
    identifiers = ma.Dict(required=True)

    class Meta:
        type_ = "compounds"
        model = Compound
        sqla_session = db.session
        load_instance = True


# TODO: create a new schema for results. It needs to contain all
# the scoring metadata