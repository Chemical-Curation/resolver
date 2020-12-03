from flask import current_app, request
from flask_rest_jsonapi.data_layers.alchemy import SqlalchemyDataLayer


class SearchDataLayer(SqlalchemyDataLayer):
    """Sqlalchemy data layer specifically to use python sorting."""

    def get_collection(self, qs, view_kwargs, filters=None):
        """Retrieve a collection of objects through sqlalchemy

        :param QueryStringManager qs: a querystring manager to retrieve information from url
        :param dict view_kwargs: kwargs from the resource view
        :param dict filters: A dictionary of key/value filters to apply to the eventual query
        :return tuple: the number of object and the list of objects
        """
        self.before_get_collection(qs, view_kwargs)

        query = self.query(view_kwargs)

        if filters:
            query = query.filter_by(**filters)

        if qs.filters:
            query = self.filter_query(query, qs.filters, self.model)

        object_count = query.count()

        # todo: limit generic searches?
        # if object_count > current_app.config['MAX_SEARCHED_ENTRIES']:
        #     raise Exception

        if getattr(self, "eagerload_includes", True):
            query = self.eagerload_includes(query, qs)

        collection = query.all()

        collection = self.calculate_scores(collection, qs, view_kwargs)

        collection = self.paginate_collection(collection, qs.pagination)

        return object_count, collection

    def paginate_collection(self, collection, paginate_info):
        """Paginate query according to jsonapi 1.0

        :param Query collection: sqlalchemy collection
        :param dict paginate_info: pagination information
        :return Query: the paginated query
        """
        if int(paginate_info.get("size", 1)) == 0:
            return collection

        page_size = int(paginate_info.get("size", 0)) or current_app.config["PAGE_SIZE"]

        start = 0
        if paginate_info.get("number"):
            start = (int(paginate_info["number"]) - 1) * page_size

        end = start + page_size

        collection = collection[start:end]

        return collection

    def calculate_scores(self, collection, qs, view_kwargs):
        """
        Sorts the returned records by the value returned by Substance.score_result
        It is not possible to apply the score_result hybrid method at the class level,
        so we cannot just append `.order_by(Substance.score_result(search_term).desc())`
        to the query. The score_result method only works at the row/instance level
        """
        if request.args.get("identifier") is not None:
            search_term = request.args.get("identifier")
            collection.sort(key=lambda x: x.score_result(search_term), reverse=True)

        return collection
