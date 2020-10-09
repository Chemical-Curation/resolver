from setuptools import setup, find_packages

__version__ = "0.1"

setup(
    name="api",
    version=__version__,
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "flask",
        "Flask-REST-JSONAPI",
        "flask-sqlalchemy",
        "flask-restful",
        "flask-migrate",
        "flask-jwt-extended",
        "flask-marshmallow",
        "marshmallow-sqlalchemy",
        "python-dotenv",
        "psycopg2-binary",
        "psycopg2",
        "passlib",
        "apispec[yaml]",
        "apispec-webframeworks",
    ],
    entry_points={"console_scripts": ["api = api.manage:cli"]},
)
