from ma import ma
from models.item import ItemModel
from marshmallow_sqlalchemy import ModelSchema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class ItemSchema(SQLAlchemyAutoSchema):
    
    class Meta:
        model = ItemModel
        load_only = ('store',)
        dump_only = ('id',)
        include_fk = True
