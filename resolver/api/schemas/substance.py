from resolver.models import Substance
from resolver.extensions import db
from marshmallow_jsonapi.schema import Schema
from marshmallow_jsonapi import fields
from marshmallow import pre_dump


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
    # the score will be calculated in the resolver
    # https://github.com/Chemical-Curation/chemcurator_django/issues/144
    search_score = fields.Raw(dump_only=True)

    @pre_dump(pass_many=True)
    def attach_search_term(self, data, **_):
        print("--- pre_dump method attach_search_term ---")
        for r in data:
            print(r.__dict__)
        return data

    def score_matches(self, substance, **view_kwargs):
        idfield = "fieldname"
        idscore = 0.90
        return "{}, {}".format(idfield, idscore)

    class Meta:
        type_ = "substance_search_results"
        model = Substance
        sqla_session = db.session
        load_instance = True
