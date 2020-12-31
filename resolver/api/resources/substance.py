from flask import request
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB

from resolver.api.data_layers import SearchDataLayer
from resolver.api.schemas import SubstanceSchema, SubstanceSearchResultSchema
from resolver.models import Substance
from resolver.extensions import db
from sqlalchemy.sql.expression import or_  # , literal_column

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


class SubstanceIndexResource(ResourceList):
    """Create and Update an indexed substance

    ---
    patch:
      tags:
        - substance_index
      requestBody:
        content:
          application/vnd.api+json:
            schema:
              allOf:
                - type: object
                  properties:
                    data:
                      type: object
                      properties:
                        type:
                          type: string
                          example: substance
                        id:
                          type: string
                          example: DTXSID1020000000
                        attributes:
                          type: object
                          properties:
                            identifier:
                              type: object
      responses:
        201:
          content:
            application/vnd.api+json:
              schema:
                allOf:
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          type:
                            type: string
                            example: substance
                          id:
                            type: sid
                            example: DTXSID1020000000
                          attributes:
                            type: object
                            properties:
                              identifier:
                                type: object
    delete:
      tags:
        - substance_index
      responses:
        200:
          content:
            application/vnd.api+json:
              schema:
                allOf:
                  - type: object
                    properties:
                      meta:
                        type: object
                        properties:
                          message:
                            type: string
                            example: Database successfully cleared. __rows__ rows deleted
    """

    schema = SubstanceSchema
    data_layer = {"session": db.session, "model": Substance}
    methods = ["POST", "DELETE"]

    def create_object(self, data, kwargs):
        """Creates or updates a model object

        Note:
            This is a limited extension of
            `flask_rest_jsonapi/data_layers/alchemy.py`
            to allow for merges.
            This will not handle relationships as there is no foreseeable need.

        Args:
            :param dict data: the data validated by marshmallow
            :param dict kwargs: kwargs from the resource view

        Returns:
            :return DeclarativeMeta: an object from sqlalchemy
        """

        obj = self._data_layer.model(**data)
        self._data_layer.session.merge(obj)
        self._data_layer.session.commit()
        return obj

    def delete(self):
        """Delete an object"""
        rows_deleted = self.delete_db()

        result = {
            "meta": {
                "message": f"Substance Index successfully cleared. {rows_deleted} rows deleted"
            }
        }

        return result

    def delete_db(self):
        rows_deleted = self._data_layer.model.query.delete()
        self._data_layer.session.commit()

        return rows_deleted


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

            # This allows reference to the aliased results from synonym select_from jsonb_array_elements
            val = db.column("value", type_=JSONB)
            # Construct synonym subquery.
            synonym_subquery = (
                self.session.query(Substance.id)
                .select_from(
                    Substance,
                    func.jsonb_array_elements(Substance.identifiers["synonyms"]),
                )
                .filter(val["identifier"].astext.ilike(f"{search_term}"))
                .subquery()
            )

            query_ = self.session.query(Substance,).filter(
                or_(
                    Substance.identifiers["preferred_name"].astext.ilike(
                        f"{search_term}"
                    ),
                    Substance.identifiers["inchikey"].astext.ilike(f"{search_term}"),
                    Substance.identifiers["compound_id"].astext.ilike(search_term),
                    Substance.id.ilike(search_term),
                    Substance.identifiers["casrn"].astext.ilike(f"{search_term}"),
                    Substance.identifiers["display_name"].astext.ilike(
                        f"{search_term}"
                    ),
                    Substance.id.in_(synonym_subquery),
                )
            )
        return query_

    def after_get(self, result):
        # Remove Pagination
        result.pop("links", None)
        return result

    methods = ["GET"]
    schema = SubstanceSearchResultSchema
    # get_schema_kwargs = {"identifier": ("identifier",)}
    data_layer = {
        "class": SearchDataLayer,
        "session": db.session,
        "model": Substance,
        "methods": {
            "query": query,
        },
    }
