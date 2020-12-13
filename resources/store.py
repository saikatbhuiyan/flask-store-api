import sqlite3
from flask import Flask, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from schemas.store import StoreSchema
from models.store import StoreModel

store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)


class Store(Resource):

    @classmethod
    @jwt_required
    def get(cls, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.dump(store)

        return {"message": "Store not found"}, 404

    @classmethod
    @jwt_required
    def post(cls):
        store_data = store_schema.load(request.get_json())
        if StoreModel.find_by_name(store_data['name']):
            return {
                "message": "An store with name '{}' already exists.".format(
                    store_data['name']
                )
            }, 400
        try:
            store = StoreModel(**store_data)
            store.save_to_db()
        except:
            return {"message": "An error occurred inserting the store."}, 500
        
        return store_schema.dump(store), 201

    @classmethod
    @jwt_required
    def delete(cls, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {"message": "Store deleted"}

    @classmethod
    @jwt_required
    def put(cls, name):
        store_json = request.get_json()

        store = StoreModel.find_by_name(name)

        if store is None:
            store = StoreModel(name)
        else:
            store_json["name"] = name
            
            try:
                store = store_schema.load(store_json)
                    
            except ValidationError as err:
                return err.messages, 400
            
        store.save_to_db()

        return store_schema.dump(store), 200


class StoreList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        user = get_jwt_identity()
        print(user)
        return {"stores": store_list_schema.dump(StoreModel.find_all())}
