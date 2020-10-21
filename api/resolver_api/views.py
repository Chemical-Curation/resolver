from flask import Blueprint, current_app, jsonify
from flask_rest_jsonapi import Api
from marshmallow import ValidationError
from api.extensions import apispec
from api.resolver_api.resources import (
    UserResource,
    UserList,
    SubstanceResource,
    SubstanceList,
    SubstanceSearch,
)
from api.resolver_api.schemas import (
    UserSchema,
    SubstanceSchema,
    SubstanceSearchResultSchema,
)

def make_api(app):
    api = Api(app=app)
    api.route(UserList, "user_list", "/users")
    api.route(UserResource, "user_detail", "/users/<int:id>")
    api.route(SubstanceList, "substance_list", "/substances")
    api.route(SubstanceResource, "substance_detail", "/substances/<id>")

    #  is this jsonapi?  If not this should be treated differently
    api.route(SubstanceSearch, "resolved_substances", "/resolver")


# @blueprint.before_app_first_request
# def register_views():
#     apispec.spec.components.schema("UserSchema", schema=UserSchema)
#     apispec.spec.path(view=UserResource, app=current_app)
#     apispec.spec.path(view=UserList, app=current_app)
#
#     apispec.spec.components.schema("SubstanceSchema", schema=SubstanceSchema)
#     apispec.spec.path(view=SubstanceResource, app=current_app)
#     apispec.spec.path(view=SubstanceList, app=current_app)
#
#     apispec.spec.components.schema(
#         "SubstanceSearchResultSchema", schema=SubstanceSearchResultSchema
#     )
#
#
# @blueprint.errorhandler(ValidationError)
# def handle_marshmallow_error(e):
#     """Return json error for marshmallow validation errors.
#
#     This will avoid having to try/catch ValidationErrors in all endpoints, returning
#     correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
#     """
#     return jsonify(e.messages), 400
