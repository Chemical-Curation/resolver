from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError
from api.extensions import apispec
from api.api.resources import (
    UserResource,
    UserList,
    CompoundResource,
    CompoundList,
    CompoundSearch,
)
from api.api.schemas import UserSchema, CompoundSchema


blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint)


api.add_resource(UserResource, "/users/<int:user_id>", endpoint="user_by_id")
api.add_resource(UserList, "/users", endpoint="users")

api.add_resource(
    CompoundResource, "/compounds/<compound_id>", endpoint="compound_by_id"
)
api.add_resource(CompoundList, "/compounds", endpoint="compounds")

api.add_resource(
    CompoundSearch, "/resolver/<search_term>", endpoint="resolved_compounds"
)


@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("UserSchema", schema=UserSchema)
    apispec.spec.path(view=UserResource, app=current_app)
    apispec.spec.path(view=UserList, app=current_app)

    apispec.spec.components.schema("CompoundSchema", schema=CompoundSchema)
    apispec.spec.path(view=CompoundResource, app=current_app)
    apispec.spec.path(view=CompoundList, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
