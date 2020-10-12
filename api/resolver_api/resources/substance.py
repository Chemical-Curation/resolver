from flask import request
from flask_restful import Resource
from api.resolver_api.schemas import SubstanceSchema, SubstanceSearchResultSchema
from api.models import Substance
from api.extensions import db
from api.commons.pagination import paginate
from sqlalchemy.sql.expression import or_

from flask_rest_jsonapi import Api, ResourceDetail, ResourceList
from flask_rest_jsonapi.exceptions import ObjectNotFound


class SubstanceResource(ResourceDetail):
    """Single object resource

    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: substance_id
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  substance: SubstanceSchema
        404:
          description: substance does not exist
    put:
      tags:
        - api
      parameters:
        - in: path
          name: substance_id
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              SubstanceSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: substance updated
                  substance: SubstanceSchema
        404:
          description: substance does not exist
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: substance_id
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: substance deleted
        404:
          description: substance does not exist
    """

    # method_decorators = [jwt_required]

    def get(self, substance_id):
        schema = SubstanceSchema()
        substance = Substance.query.get_or_404(substance_id)
        return {"substance": schema.dump(substance)}

    def put(self, substance_id):
        schema = SubstanceSchema(partial=True)
        substance = Substance.query.get_or_404(substance_id)
        substance = schema.load(request.json, instance=substance)

        db.session.commit()

        return {"msg": "substance updated", "substance": schema.dump(substance)}

    def delete(self, substance_id):
        substance = Substance.query.get_or_404(substance_id)
        db.session.delete(substance)
        db.session.commit()

        return {"msg": "substance deleted"}


class SubstanceList(ResourceList):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResult'
                  - type: object
                    properties:
                      results:
                        type: array
                        items:
                          $ref: '#/components/schemas/SubstanceSchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              SubstanceSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: substance created
                  substance: SubstanceSchema
    """

    # method_decorators = [jwt_required]

    def get(self):
        schema = SubstanceSchema(many=True)
        query = Substance.query
        return paginate(query, schema)

    def post(self):
        schema = SubstanceSchema()
        substance = schema.load(request.json)

        db.session.add(substance)
        db.session.commit()

        return {"msg": "substance created", "substance": schema.dump(substance)}, 201


class SubstanceSearch(Resource):
    """

    ---
    get:
      tags:
        - api
      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResult'
                  - type: object
                    properties:
                      results:
                        type: array
                        items:
                          $ref: '#/components/schemas/SubstanceSearchResultSchema'
    """

    def get(self):
        schema = SubstanceSearchResultSchema(many=True)
        # PostgreSQL cheat sheet:
        # https://medium.com/hackernoon/how-to-query-jsonb-beginner-sheet-cheat-4da3aa5082a3

        if request.args:
            args = request.args
            search_term = args["identifier"]
            query = Substance.query.filter(
                or_(
                    Substance.identifiers["preferred_name"].astext.contains(
                        search_term
                    ),
                    Substance.identifiers["casrn"].astext.contains(search_term),
                    Substance.identifiers["display_name"].astext.contains(search_term),
                )
            )
            return paginate(query, schema)
        else:
            return {
                "msg": "no search string provided",
            }
