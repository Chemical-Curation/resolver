from api.models import Compound
from api.extensions import ma, db


class CompoundSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Str(dump_only=True)
    password = ma.String(load_only=True, required=True)

    class Meta:
        model = Compound
        sqla_session = db.session
        load_instance = True
