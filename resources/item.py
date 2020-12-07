import sqlite3
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity,
    jwt_optional,
    fresh_jwt_required,
)

# from security import authenticate, identity
from models.item import ItemModel


BLANK_ERROR = "'{}' cannot be blank!"
ITEM_NOT_FOUND = "Item not found"

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "name", type=str, required=True, help=BLANK_ERROR.format('name')
    )
    parser.add_argument(
        "price", type=float, required=True, help=BLANK_ERROR.format('price')
    )
    parser.add_argument(
        "store_id", type=int, required=True, help=BLANK_ERROR.format('store_id')
    )

    @classmethod
    def get(cls, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @jwt_required
    def post(cls):
        data = Item.parser.parse_args()
        if ItemModel.find_by_name(data["name"]):
            return {
                "message": "An item with name '{}' already exists.".format(data["name"])
            }, 400
        item = ItemModel(**data)
        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred inserting the item."}, 500

        return item.json(), 201

    @classmethod
    @jwt_required
    def delete(cls, name):
        claims = get_jwt_claims()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required."}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {"message": "Item deleted"}

    @classmethod
    @jwt_required
    def put(cls, name):
        data = Item.parser.parse_args()
        # Once again, print something not in the args to verify everything works

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, data["price"], data["store_id"])
        else:
            item.price = data["price"]

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    @classmethod
    def get(cls):
        return {"items": [item.json() for item in ItemModel.find_all()]}, 200

    # return {"items": [item.json() for item in ItemModel.query.all()]}
    # return {"items": list(map(lambda item: item.json, ItemModel.query.all()))}
