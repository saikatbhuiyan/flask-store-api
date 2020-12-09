from ma import ma
from models.store import StoreModel
from models.item import ItemModel
from .item import ItemSchema
# from marshmallow_sqlalchemy import ModelSchema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class StoreSchema(SQLAlchemyAutoSchema):
    items = ma.Nested(ItemSchema, many=True)

    class Meta:
        model = StoreModel
        load_only = ('user',)
        dump_only = ('id',)
        include_fk = True
