import sqlite3
from flask import Flask, request
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity,
    jwt_optional,
    fresh_jwt_required,
)
from marshmallow import ValidationError

from models.item import ItemModel
from schemas.item import ItemSchema

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


BLANK_ERROR = "'{}' cannot be blank!"
ITEM_NOT_FOUND = "Item not found"

class Item(Resource):

    @classmethod
    def get(cls, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @jwt_required
    def post(cls):
        item = item_schema.load(request.get_json())
        if ItemModel.find_by_name(item['name']):
            return {
                "message": "An item with name '{}' already exists.".format(item['name'])
            }, 400
        item = ItemModel(**item)
        item.save_to_db()
   
        return item_schema.dump(item), 201

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
        item_json = request.get_json()
        # Once again, print something not in the args to verify everything works

        item = ItemModel.find_by_name(name)

        if item is None:
            item.price = item_json['price']
        else:
            item_json['name'] = name
            
            try:
                item = item_schema.load(item_json)
                
            except ValidationError as err:
                return err.messages, 400
            
        item.save_to_db()

        return item_schema.dump(item), 200


class ItemList(Resource):
    
    @classmethod
    def get(cls):
        return {"items": item_list_schema.dump(ItemModel.find_all())}, 200
