from flask import Flask, jsonify
from flask_restful import Api

# from flask_jwt import JWT, current_identity
from flask_jwt_extended import JWTManager

from marshmallow import ValidationError

# from security import authenticate, identity
from resources.user import (
    UserRegister, 
    User, 
    UserLogin, 
    UserLogout, 
    TokenRefresh,
    UserConfirm,
)
from resources.item import (Item, ItemList)
from resources.store import Store, StoreList
from _datetime import timedelta
from blacklist import BLACKLIST



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"  # set db to root
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True  # this is return the proper error to us
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
app.secret_key = "sami"
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()  # Store -> StoreModel



# config JWT auth key name to be 'email' instead of default 'username'
# app.config['JWT_AUTH_USERNAME_KEY'] = 'email'

# config JWT to expire within half an hour
app.config["JWT_EXPIRATION_DELTA"] = timedelta(seconds=1800)

# app.config['JWT_AUTH_URL_RULE'] = '/login'
# jwt = JWT(app, authenticate, identity) # default /auth


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400

jwt = JWTManager(app)  # not creating /auth

# @jwt.user_claims_loader
# def add_claims_to_jwt(identity):
#   if identity == 1:
#     return {"is_admin": True}
#   return {"is_admin": False}


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST


# @jwt.expired_token_loader
# def expired_token_callback():
#   return jsonify({
#     'message': 'Your session has been end',
#     'error': 'token_expired'
#   }), 401

# @jwt.invalid_token_loader
# def invalid_token_callback(error):
#   return jsonify({
#     "message": "Signature verification failed",
#     "error": "invalid_token"
#   }), 401

# @jwt.unauthorized_loader
# def missing_token_callback(error):
#   return jsonify({
#     "message": "Request does not contains an access token",
#     "error": "authorization_required"
#   }), 401

# @jwt.needs_fresh_token_loader
# def token_not_fresh_callback():
#   return jsonify({
#       "message": "The token is not fresh",
#       "error": "fresh_token_required"
#     }), 401

# @jwt.revoked_token_loader
# def revoked_token_callback():
#   return jsonify({
#       "message": "The token has been revoked",
#       "error": "token_revoked"
#     }), 401


api.add_resource(Store, "/store")
api.add_resource(StoreList, "/stores")
api.add_resource(Item, "/item")
api.add_resource(ItemList, "/items")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserConfirm, "/user_confirm/<int:user_id>")


if __name__ == "__main__":
    from db import db
    from ma import ma

    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True)
