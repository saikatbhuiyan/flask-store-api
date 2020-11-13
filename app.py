from flask import Flask
from flask_restful import Api
# from flask_jwt import JWT, current_identity
from flask_jwt_extended import JWTManager

# from security import authenticate, identity
from resources.user import UserRegister, User, UserLogin
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from _datetime import timedelta

 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db' # set db to root
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True # this is return the proper error to us 
app.secret_key = 'sami'
api = Api(app)

@app.before_first_request
def create_tables():
  db.create_all() # Store -> StoreModel

# config JWT auth key name to be 'email' instead of default 'username'
# app.config['JWT_AUTH_USERNAME_KEY'] = 'email'

# config JWT to expire within half an hour
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)

# app.config['JWT_AUTH_URL_RULE'] = '/login'
# jwt = JWT(app, authenticate, identity) # default /auth
jwt = JWTManager(app) # not creating /auth


api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')


if __name__ == '__main__':
  from db import db
  db.init_app(app)
  app.run(port=5000, debug=True)