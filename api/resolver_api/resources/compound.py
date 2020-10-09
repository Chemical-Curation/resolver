from flask import request
from flask_restful import Resource
from api.resolver_api.schemas import CompoundSchema
from api.models import Compound
from api.extensions import db
from api.commons.pagination import paginate


class CompoundResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: compound_id
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  compound: CompoundSchema
        404:
          description: compound does not exist
    put:
      tags:
        - api
      parameters:
        - in: path
          name: compound_id
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              CompoundSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: compound updated
                  compound: CompoundSchema
        404:
          description: compound does not exist
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: compound_id
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
                    example: compound deleted
        404:
          description: compound does not exist
    """

    # method_decorators = [jwt_required]

    def get(self, compound_id):
        schema = CompoundSchema()
        compound = Compound.query.get_or_404(compound_id)
        return {"compound": schema.dump(compound)}

    def put(self, compound_id):
        schema = CompoundSchema(partial=True)
        compound = Compound.query.get_or_404(compound_id)
        compound = schema.load(request.json, instance=compound)

        db.session.commit()

        return {"msg": "compound updated", "compound": schema.dump(compound)}

    def delete(self, compound_id):
        compound = Compound.query.get_or_404(compound_id)
        db.session.delete(compound)
        db.session.commit()

        return {"msg": "compound deleted"}


class CompoundList(Resource):
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
                          $ref: '#/components/schemas/CompoundSchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              CompoundSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: compound created
                  compound: CompoundSchema
    """

    # method_decorators = [jwt_required]

    def get(self):
        schema = CompoundSchema(many=True)
        query = Compound.query
        return paginate(query, schema)

    def post(self):
        schema = CompoundSchema()
        compound = schema.load(request.json)

        db.session.add(compound)
        db.session.commit()

        return {"msg": "compound created", "compound": schema.dump(compound)}, 201


class CompoundSearch(Resource):
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
                          $ref: '#/components/schemas/CompoundSchema'
    """

    def get(self, search_term):
        schema = CompoundSchema(many=True)
        # PostgreSQL cheat sheet:
        # https://medium.com/hackernoon/how-to-query-jsonb-beginner-sheet-cheat-4da3aa5082a3
        query = Compound.query.filter(
            Compound.identifiers["preferred_name"].astext.contains(search_term)
        )

        return paginate(query, schema)
