# from marshmallow import Schema, fields
from marshmallow_sqlalchemy import ModelSchema


# class UserSchema(Schema):
#     id = fields.Int()
#     username = fields.Str(required=True)
#     password = fields.Str(required=True)
    
#     class Meta:
#         load_only = ('password',)

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from ma import ma
from models.user import UserModel
from .store import StoreSchema

class UserSchema(SQLAlchemyAutoSchema):
    stores = ma.Nested(StoreSchema, many=True)

    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id",)
        include_fk = True
