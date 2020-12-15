from ma import ma
from models.order import OrderModel
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class OrderSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = OrderModel
        load_only = ("token",)
        dump_only = ("id", "status",)