import sqlite3
import datetime
from werkzeug.security import safe_str_cmp
from flask_restful import Resource, reqparse
from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    jwt_required,
    get_raw_jwt,
)

from sqlalchemy import engine
from sqlalchemy.orm import scoped_session, sessionmaker

from marshmallow import ValidationError
from models.user import UserModel
from blacklist import BLACKLIST

from schemas.user import UserSchema


user_schema = UserSchema()

class UserRegister(Resource):
    
    @classmethod
    def post(cls):
        user = user_schema.load(request.get_json())

        if UserModel.find_by_username(user["username"]):
            return {"message": "User already exists"}, 400

        user = UserModel(**user)
        user.save_to_db()

        return {"message": "User created successfully."}, 201


class User(Resource):
    
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        
        if not user:
            return {"message": "User not found"}, 404

        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 404
        
        user.delete_from_db()
        
        return {"message": "User delete"}, 200


class UserLogin(Resource):
    
    @classmethod
    def post(cls):
        try:
            user_data = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        user = UserModel.find_by_username(user_data['username'])

        if user and safe_str_cmp(user.password, user_data['password']):
            expires = datetime.timedelta(seconds=3600)
            access_token = create_access_token(
                identity=user.id, expires_delta=expires, fresh=True
            )
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": "Invalid credentials"}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out."}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        expires = datetime.timedelta(seconds=3600)
        new_token = create_access_token(
            identity=current_user, expires_delta=expires, fresh=False
        )
        return {"access_token": new_token}, 200
