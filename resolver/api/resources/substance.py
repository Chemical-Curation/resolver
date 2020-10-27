from flask import request
from resolver.api.schemas import SubstanceSchema, SubstanceSearchResultSchema
from resolver.models import Substance
from resolver.extensions import db
from resolver.commons.pagination import paginate
from sqlalchemy.sql.expression import or_
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

from flask_rest_jsonapi import ResourceDetail, ResourceList


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

    schema = SubstanceSchema
    data_layer = {"session": db.session, "model": Substance}


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

    schema = SubstanceSchema
    data_layer = {"session": db.session, "model": Substance}


class SubstanceSearchResultList(ResourceList):
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

    def query(self, view_kwargs):
        query_ = self.session.query(Substance)
        if request.args.get("identifier") is not None:
            search_term = request.args.get("identifier")
            try:
                # make sure the query returns something
                Substance.query.filter(
                    or_(
                        Substance.identifiers["preferred_name"].astext.contains(
                            search_term
                        ),
                        Substance.identifiers["casrn"].astext.contains(search_term),
                        Substance.identifiers["display_name"].astext.contains(
                            search_term
                        ),
                    )
                ).one()
            except NoResultFound:
                # TODO: should this return a 200 code but with an empty [] array?
                raise ObjectNotFound(
                    {"parameter": "identifier"},
                    "Identifer {} did not resolve to a substance".format(
                        request.args["identifier"]
                    ),
                )
            else:
                query_ = self.session.query(Substance).filter(
                    or_(
                        Substance.identifiers["preferred_name"].astext.contains(
                            search_term
                        ),
                        Substance.identifiers["casrn"].astext.contains(search_term),
                        Substance.identifiers["display_name"].astext.contains(
                            search_term
                        ),
                    )
                )
        return query_

    methods = ["GET"]
    schema = SubstanceSearchResultSchema
    # get_schema_kwargs = {"identifier": ("identifier",)}
    data_layer = {
        "session": db.session,
        "model": Substance,
        "methods": {"query": query},
    }
