FROM python:3.8

RUN mkdir /code
WORKDIR /code

COPY requirements.txt setup.py tox.ini ./
RUN pip install -r requirements.txt
RUN pip install -e .

COPY resolver resolver/

EXPOSE 5000

ENTRYPOINT ["resolver/docker-entrypoint.sh"]
