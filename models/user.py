import sqlite3
from db import db

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def json(self):
        return {'id': self.id, 'username': self.username}

    @classmethod
    def find_by_username(cls, username):
        # here query is euery builder
        return cls.query.filter_by(username=username).first() 
        
        # connection = sqlite3.connect('data.db')
        # cursor = connection.cursor()

        # query = "SELECT * FROM users WHERE username=?"
        # result = cursor.execute(query, (username,))
        # row = result.fetchone() # get first row else none
        # if row:
        #     # user = User(row[0], row[1], row[2])
        #     user = cls(*row)
        # else: 
        #     user = None

        # connection.close()
        # return user

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first() # here query is euery builder

        # connection = sqlite3.connect('data.db')
        # cursor = connection.cursor()

        # query = "SELECT * FROM users WHERE id=?"
        # result = cursor.execute(query, (_id,))
        # row = result.fetchone() # get first row else none
        # if row:
        #     user = cls(*row)
        # else: 
        #     user = None

        # connection.close()
        # return user
  
    def save_to_db(self):
      db.session.add(self)
      db.session.commit()     

    def delete_from_db(self):
      db.session.delete(self)
      db.session.commit()   