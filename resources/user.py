import datetime
import traceback
from werkzeug.security import safe_str_cmp
from flask_restful import Resource, reqparse
from flask import request, make_response, render_template
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
from libs.mailgun import MailGunException

USER_ALREADY_EXISTS = "A user with this username already exists"
EMAIL_ALREADY_EXISTS = "A user with that email already exists."
USER_NOT_CONFIRMED = "You have not confirmed registration, Please check your email <{}>."
USER_CREATED = "User created successfully."
USER_NOT_FOUND = "User not found."
USER_CONFIRMED = "User Confirmed."
FAILED_TO_CREATE = "Internal server error. Failed to create user."
SUCCESS_REGISTER_MESSAGE = "Account created successfully, an email with an activation link has been sent to your " \
                           "email address, please check. "
NOT_CONFIRMED_ERROR = (
    "You have not confirmed registration, please check your email <{}>."
)
user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user = user_schema.load(user_json)

        if UserModel.find_by_username(user["username"]):
            return {"message": USER_ALREADY_EXISTS}, 400

        if UserModel.find_by_email(user["email"]):
            return {"message": EMAIL_ALREADY_EXISTS}, 400

        try:
            user = UserModel(**user)
            user.save_to_db()
            user.send_confirmation_email()
            return {"message": SUCCESS_REGISTER_MESSAGE}, 201
        except MailGunException as e:
            user.delete_from_db()  # rollback
            return {"message": str(e)}, 500
        except:  # failed to save user to db
            traceback.print_exc()
            return {"message": FAILED_TO_CREATE}, 500


class User(Resource):

    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"message": USER_NOT_FOUND}, 404

        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404

        user.delete_from_db()

        return {"message": "User delete"}, 200


class UserLogin(Resource):

    @classmethod
    def post(cls):
        try:
            user_data = user_schema.load(request.get_json(), partial=("email",))
        except ValidationError as err:
            return err.messages, 400

        user = UserModel.find_by_username(user_data['username'])

        if user and safe_str_cmp(user.password, user_data['password']):
            if user.activated:
                expires = datetime.timedelta(seconds=3600)
                access_token = create_access_token(
                    identity=user.id, expires_delta=expires, fresh=True
                )
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200
            return {'message': USER_NOT_CONFIRMED.format(user.username)}, 400

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


class UserConfirm(Resource):

    @classmethod
    def get(cls, user_id: id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.activated = True
        user.save_to_db()
        headers = {"Content-Type": "text/html"}
        return make_response(render_template("confirmation_page.html", email=user.username), 200, headers)
