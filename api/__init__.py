from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB

app = Flask(__name__)
app.config.from_object("api.config.Config")
db = SQLAlchemy(app)


class Compound(db.Model):
    __tablename__ = "compounds"

    id = db.Column(db.String(128), primary_key=True)
    identifiers = db.Column(JSONB)

    def __init__(self, id, identifiers):
        self.id = id
        self.identifiers = identifiers


@app.route("/")
def hello_world():
    return jsonify(hello="world")