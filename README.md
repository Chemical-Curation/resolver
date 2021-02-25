# resolver

# Resolver developer setup

## Installing the application

This application was installed using [cookiecutter-flask-restful](https://github.com/karec/cookiecutter-flask-restful).  If anything seems unclear about the installation project, the source repo may be able to provide additional guidance.

### Create an anaconda environment
Feel free to use whatever environment software you wish.  To get started with [Anaconda](https://docs.anaconda.com/anaconda/install/) use the commands below.
```
conda create -n resolver python=3.8
conda activate resolver

pip install -r requirements.txt
pip install -e .
```
The first 2 commands will create an Anaconda environment named resolver using python 3.8 and then activate it.

`pip install -r requirements.txt` installs the project dependencies.

`pip install -e .` installs the project on the machine.  This allows you to interface with the application by using the installed name, currently `resolver`, rather than using it through Flask.  It also makes `resolver/manage.py` an entry point into the application and allows for the addition of custom management commands.

### Create environment files
Make a `.flaskenv` and the `.testenv` from the `template.flaskenv` and `template.testenv`.

### Create Docker Pods
Use [docker-compose](https://docs.docker.com/compose/) to build pods for running.
```
docker-compose build
docker-compose up
```

### Initialize Flask Application
Run the commands that will initialize the resolver application.
```
resolver initdb
resolver db upgrade
resolver init
resolver run
```

`resolver initdb` uses [SQLAlchemy-Utils](https://github.com/kvesteri/sqlalchemy-utils) checks to verify whether or not the database that is currently being used exists.  Given a DATABASE_URI of `postgresql://postgres@localhost/name`, This will attempt to connect to localhost as user postgres and verify that the database `name` exists.  If it does not it will create it.

`resolver db upgrade` applies all outstanding migrations to bring the database up to date.

`resolver init` readies the database for use.  This may include loading seed data or adding a initial user.

`resolver run` starts the application running in development mode.  The app is started on http://127.0.0.1:5000/ unless otherwise specified

### Syncing with Chemcurator
In the `chemcurator_django` directory, run `python manage.py sync` to load all the Chemcurator substances into the resolver. 

### Testing
[pytest](https://docs.pytest.org/en/stable/) is the testing framework currently being used.  Tests can be run using pytest directly with the command `pytest` or using [tox](https://tox.readthedocs.io/en/latest/) with the command `tox`.  

Tox runs the environment in a venv and installs all dependencies locally.  To recreate a tox environment run `tox -r` and to bypass the linting portion run `tox -e test`

## Structural Overview

A high-level overview of the resolver repo looks something like this.

```
migrations/          # Alembic/SQLAlchemy migrations
├─ versions/
│  ├─ migration.py
resolver/            # Main Application within Resolver
├─ api/                  # Code to deal with handling requests
│  ├─ resources/             # Similar to django's views.  Handles requests
│  ├─ schemas/               # Similar to django-rest-framework's serializers.  Translates a model to a json representation and vice versa.
│  ├─ views.py               # Similar to django's urls.  Creates routing from a url to a resource
├─ auth/                 # Authentication endpoints and processing.  Similar to the above api folder but for authentication and authorization
├─ commons/              # Code that is across the resolver app.
├─ models/               # Class representations of tables.
├─ app.py                # Creates the application.  See function `resolver.app.create_app()`
├─ config.py             # Loads .env variables for use across the app.
├─ extentions.py         # Extentions to be used as singletons. Instantiated by `resolver.app.create_app()`
├─ manage.py             # Entry point when interfacing with resolver through the command line.  Built using {{repo_root}}/setup.py
├─ wsgi.py               # Calls `resolver.app.create_app()`
tests/               #Tests
├─ conftest.py           # Builds pytest app.  Sets up fixtures to be used in tests.
├─ fakers.py             # Custom faker providers
├─ factories.py          # Factories for models
```
