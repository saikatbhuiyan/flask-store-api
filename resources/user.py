import sqlite3
from flask_restful import Resource, reqparse 

from models.user import UserModel

# class User(object):
#     def __init__(self, _id, username, password):
#         self.id = _id
#         self.username = username
#         self.password = password

#     @classmethod
#     def find_by_username(cls, username):
#         connection = sqlite3.connect('data.db')
#         cursor = connection.cursor()

#         query = "SELECT * FROM users WHERE username=?"
#         result = cursor.execute(query, (username,))
#         row = result.fetchone() # get first row else none
#         if row:
#             # user = User(row[0], row[1], row[2])
#             user = cls(*row)
#         else: 
#             user = None

#         connection.close()
#         return user

#     @classmethod
#     def find_by_id(cls, _id):
#         connection = sqlite3.connect('data.db')
#         cursor = connection.cursor()

#         query = "SELECT * FROM users WHERE id=?"
#         result = cursor.execute(query, (_id,))
#         row = result.fetchone() # get first row else none
#         if row:
#             user = cls(*row)
#         else: 
#             user = None

#         connection.close()
#         return user


class UserRegister(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('username', 
        type=str,
        required=True,
        help="This field cannot be blank."
    )
    parser.add_argument('password', 
        type=str,
        required=True,
        help="This field cannot be blank."
    )

    def post(self):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "User already exists"}, 400

        # user = UserRegister(data['username'], data['password'])
        user = UserRegister(**data)
        user.save_to_db()

        return {"message": "User created successfully."}, 201
    # def post(self):
    #     data = UserRegister.parser.parse_args()

    #     if UserModel.find_by_username(data['username']):
    #         return {"message": "User already exists"}, 400

    #     connection = sqlite3.connect('data.db')
    #     cursor = connection.cursor()

    #     query = "INSERT INTO users VALUES (NULL, ?, ?)"
    #     cursor.execute(query, (data['username'], data['password']))

    #     connection.commit()
    #     connection.close()


    #     return {"message": "User created successfully."}, 201


class User(Resource):

    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
    
        return user.json()

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        user.delete_from_db()
        return {'message': 'User delete'}, 200








