from flask import Flask

from resolver import auth
from resolver.api import views as api_views
from resolver.extensions import db, jwt, migrate, apispec, init_db


def create_app(testing=False, cli=False):
    """Application factory, used to create application"""
    app = Flask("resolver")
    app.config.from_object("resolver.config")
    # this is the only place I was able to reliably set this variable
    # and avoid getting nagged about it
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if testing is True:
        app.config["TESTING"] = True

    configure_extensions(app, cli)
    configure_apispec(app)
    register_blueprints(app)

    init_db()

    return app


def configure_extensions(app, cli):
    """configure flask extensions"""
    db.init_app(app)
    jwt.init_app(app)

    if cli is True:
        migrate.init_app(app, db)


def configure_apispec(app):
    """Configure APISpec for swagger support"""
    apispec.init_app(app, security=[{"jwt": []}])
    apispec.spec.components.security_scheme(
        "jwt", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )
    apispec.spec.components.schema(
        "PaginatedResult",
        {
            "properties": {
                "total": {"type": "integer"},
                "pages": {"type": "integer"},
                "next": {"type": "string"},
                "prev": {"type": "string"},
            }
        },
    )


def register_blueprints(app):
    """register all blueprints for application"""
    app.register_blueprint(auth.views.blueprint)
    app.register_blueprint(api_views.blueprint)
    api_views.make_jsonapi(app)
