from api.models import Compound
from api.extensions import ma, db


class CompoundSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Str(required=True)
    identifiers = ma.Dict(required=True)

    class Meta:
        model = Compound
        sqla_session = db.session
        load_instance = True
