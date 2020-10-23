from flask import Blueprint, current_app, jsonify
from flask_rest_jsonapi import Api as JsonApi
from flask_restful import Api as RestfulApi
from marshmallow import ValidationError
from resolver.extensions import apispec
from resolver.api.resources import (
    UserResource,
    UserList,
    SubstanceResource,
    SubstanceList,
    SubstanceSearch,
)
from resolver.api.schemas import (
    UserSchema,
    SubstanceSchema,
    SubstanceSearchResultSchema,
)

api_versioning_v1 = "/api/v1"

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
restful_api = RestfulApi(blueprint)


restful_api.add_resource(UserList, "/users", endpoint="user_list")
restful_api.add_resource(UserResource, "/users/<int:user_id>", endpoint="user_detail")


def make_jsonapi(app):
    jsonapi = JsonApi(app=app)
    jsonapi.route(SubstanceList, "substance_list", f"{api_versioning_v1}/substances")
    jsonapi.route(SubstanceResource, "substance_detail", f"{api_versioning_v1}/substances/<id>")

    #  is this jsonapi?  If not this should be treated differently
    jsonapi.route(SubstanceSearch, "resolved_substances", f"{api_versioning_v1}/resolver")


@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("UserSchema", schema=UserSchema)
    apispec.spec.path(view=UserResource, app=current_app)
    apispec.spec.path(view=UserList, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
