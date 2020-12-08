# from marshmallow import Schema, fields


# class UserSchema(Schema):
#     id = fields.Int()
#     username = fields.Str(required=True)
#     password = fields.Str(required=True)
    
#     class Meta:
#         load_only = ('password',)

from ma import ma
from models.user import UserModel
class UserSchema(ma.ModelSchema):
    class Meta:
        model = UserModel
        load_only = ('password',)
        dump_only = ('id',)