import sqlite3
from flask import Flask, request
from flask_restful import Resource, reqparse

from models.store import StoreModel

class Store(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name',
        type=float,
        required=True,
        help="This field cannot be left blank!"
    )

    @jwt_required()
    def get(self, name):
        store = StoreModel.find_by_name(name)

        if store:
            return store.json()

        return {'message': 'Store not found'}, 404

    def post(self, name):
        if StoreModel.find_by_name(name):
            return {'message': "An store with name '{}' already exists.".format(name)}, 400
        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {"message": "An error occurred inserting the store."}, 500 
        return store.json(), 201

    @jwt_required()
    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {'message': 'Store deleted'}

    @jwt_required()
    def put(self, name):
        data = Store.parser.parse_args()

        store = StoreModel.find_by_name(name)

        if store is None: 
            store = StoreModel(name)
        else:
            store.name = data['name']

        store.save_to_db()

        return store.json()


class StoreList(Resource):

  def get(self):
      
    return {"stores": list(map(lambda store: store.json, StoreModel.query.all()))}

