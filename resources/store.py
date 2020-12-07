import sqlite3
from flask import Flask, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from models.store import StoreModel


class Store(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "name", type=str, required=True, help="This field cannot be left blank!"
    )

    @classmethod
    def get(cls, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()

        return {"message": "Store not found"}, 404

    @classmethod
    @jwt_required
    def post(cls):
        data = Store.parser.parse_args()
        if StoreModel.find_by_name(data["name"]):
            return {
                "message": "An store with name '{}' already exists.".format(
                    data["name"]
                )
            }, 400
        store = StoreModel(**data)
        try:
            store.save_to_db()
        except:
            return {"message": "An error occurred inserting the store."}, 500
        return store.json(), 201

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
        data = Store.parser.parse_args()

        store = StoreModel.find_by_name(name)

        if store is None:
            store = StoreModel(name)
        else:
            store.name = data["name"]
        store.save_to_db()

        return store.json()


class StoreList(Resource):
    @classmethod
    def get(cls):
        return {"stores": list(store.json() for store in StoreModel.find_all())}

        # return {"stores": list(map(lambda store: store.json, StoreModel.find_all()))}
