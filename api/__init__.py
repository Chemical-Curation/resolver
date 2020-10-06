from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.indexable import index_property
from sqlalchemy import text

from flask_rest_jsonapi import Api, ResourceDetail, ResourceList
from flask_rest_jsonapi.exceptions import ObjectNotFound
from flask import request
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

app = Flask(__name__)
app.config.from_object("api.config.Config")
db = SQLAlchemy(app)


class Compound(db.Model):
    __tablename__ = "compounds"
    # The identifiers field needs to be indexed
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


class CompoundSchema(Schema):
    class Meta:
        type_ = "compound"
        self_view = "compound_detail"
        self_view_kwargs = {"id": "<id>"}
        self_view_many = "compound_list"

    id = fields.Str()
    identifiers = fields.Str()


class CompoundList(ResourceList):
    schema = CompoundSchema

    data_layer = {"session": db.session, "model": Compound}


class CompoundDetail(ResourceDetail):

    schema = CompoundSchema
    data_layer = {
        "session": db.session,
        "model": Compound,
    }


api = Api(app)
api.route(CompoundList, "compound_list", "/compounds")
api.route(
    CompoundDetail,
    "compound_detail",
    "/compounds/<id>",
)


@app.route("/")
def hello_world():
    return jsonify(hello="world")


@app.route("/resolve")
def resolve():
    if request.args:
        args = request.args
        # Use the query string to search the identifiers
        # https://docs-sqlalchemy.readthedocs.io/ko/latest/dialects/postgresql.html#full-text-search
        if args["q"]:
            q = args["q"]
            print(q)

    return jsonify(resolving=args)