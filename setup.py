from setuptools import setup, find_packages

__version__ = "0.1"

setup(
    name="resolver",
    version=__version__,
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "flask",
        "Flask-REST-JSONAPI",
        "flask-sqlalchemy",
        "flask-restful",
        "flask-migrate",
        "flask-jwt-extended==3.24.1",
        "flask-marshmallow",
        "gunicorn",
        "epam.indigo",
        "marshmallow-sqlalchemy",
        "python-dotenv",
        "psycopg2-binary",
        "passlib",
        "apispec[yaml]",
        "apispec-webframeworks",
    ],
    entry_points={"console_scripts": ["resolver = resolver.manage:cli"]},
)
