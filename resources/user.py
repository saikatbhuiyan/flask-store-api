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

from marshmallow import ValidationError
from models.user import UserModel
from models.confirmation import ConfirmationModel
from blacklist import BLACKLIST

from schemas.user import UserSchema
from libs.mailgun import MailGunException
from libs.strings import gettext

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user = user_schema.load(user_json)

        if UserModel.find_by_username(user["username"]):
            return {"message": gettext("user_username_exists")}, 400

        if UserModel.find_by_email(user["email"]):
            return {"message": gettext("user_email_exists")}, 400
        user = UserModel(**user)

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": gettext("user_registered")}, 201
        except MailGunException as e:
            user.delete_from_db()  # rollback
            return {"message": str(e)}, 500
        except:  # failed to save user to db
            traceback.print_exc()
            user.delete_from_db()  # rollback
            return {"message": gettext("user_error_creating")}, 500


class User(Resource):

    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"message":  gettext("user_not_found")}, 404

        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message":  gettext("user_not_found")}, 404

        user.delete_from_db()

        return {"message": gettext("user_deleted")}, 200


class UserLogin(Resource):

    @classmethod
    def post(cls):
        try:
            user_data = user_schema.load(request.get_json(), partial=("email",))
        except ValidationError as err:
            return err.messages, 400

        user = UserModel.find_by_username(user_data['username'])

        if user and safe_str_cmp(user.password, user_data['password']):
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                expires = datetime.timedelta(seconds=3600)
                access_token = create_access_token(
                    identity=user.id, expires_delta=expires, fresh=True
                )
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200
            return {'message': gettext("user_not_confirmed").format(user.email)}, 400

        return {"message": gettext("user_invalid_credentials")}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": gettext("user_logged_out").format(user_id)}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        expires = datetime.timedelta(seconds=3600)
        new_token = create_access_token(
            identity=current_user, expires_delta=expires, fresh=False
        )
        return {"access_token": new_token}, 200


# class UserConfirm(Resource):
#
#     @classmethod
#     def get(cls, user_id: id):
#         user = UserModel.find_by_id(user_id)
#         if not user:
#             return {"message": USER_NOT_FOUND}, 404
#         user.activated = True
#         user.save_to_db()
#         headers = {"Content-Type": "text/html"}
#         return make_response(render_template("confirmation_page.html", email=user.username), 200, headers)
