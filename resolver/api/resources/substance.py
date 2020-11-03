from flask import request
from sqlalchemy import func

from resolver.api.schemas import SubstanceSchema, SubstanceSearchResultSchema
from resolver.models import Substance
from resolver.extensions import db
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

    # todo: remove.  This is a sample query to hopefully save me from forgetting it.
    # Substance.query.select_from(Substance, func.jsonb_array_elements(Substance.identifiers['synonyms']).alias()).filter(Substance.val['identifier'].astext.contains("sonfwonaofw")).all()

    def query(self, view_kwargs):
        query_ = self.session.query(Substance)
        if request.args.get("identifier") is not None:
            search_term = request.args.get("identifier")
            query_ = self.session.query(Substance).select_from(Substance, func.jsonb_array_elements(Substance.identifiers['synonyms']).alias()).filter(
                or_(
                    Substance.identifiers["preferred_name"].astext.ilike(
                        f"%{search_term}%"
                    ),
                    Substance.identifiers["casrn"].astext.ilike(f"%{search_term}%"),
                    Substance.identifiers["display_name"].astext.ilike(
                        f"%{search_term}%"
                    ),
                    Substance.val['identifier'].astext.ilike(f"%{search_term}%")
                )
            )
        return query_

    def after_get_collection(self, collection, qs, view_kwargs):
        """
        TODO: Scoring the members of the collection could happen here
        See https://github.com/Chemical-Curation/chemcurator_django/issues/144
        This method could also populate the `matches` field in the serialized
        SubstanceSearchResultSchema
        """
        pass

    methods = ["GET"]
    schema = SubstanceSearchResultSchema
    # get_schema_kwargs = {"identifier": ("identifier",)}
    data_layer = {
        "session": db.session,
        "model": Substance,
        "methods": {
            "query": query,
            # "after_get_collection": after_get_collection,
        },
    }
