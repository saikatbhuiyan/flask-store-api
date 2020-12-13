from ma import ma
from models.confirmation import ConfirmationModel
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class ConfirmationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ConfirmationModel
        load_only = ("user",)
        dump_only = ("id", "expired_at", "confirmed")
        include_fk = True
