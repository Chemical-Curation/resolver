FLASK_ENV=development
FLASK_APP=api.app:create_app
SECRET_KEY=changeme

# The POSTGRES_* variables are required by the docker-compose file
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=resolver

# The postgres bouncer is using these variables to connect:
SQL_HOST=127.0.0.1
SQL_PASSWORD=postgres
SQL_PORT=5431
SQL_USER=postgres
# The redundancy should be tidied up

# The server is using 5431 to avoid conflicts with other apps
DATABASE_URI=postgresql://postgres:postgres@127.0.0.1:5431/resolver