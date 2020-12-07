import sqlite3
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import (
    jwt_required, 
    get_jwt_claims, 
    get_jwt_identity, 
    jwt_optional,
    fresh_jwt_required
)

# from security import authenticate, identity
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name',
        type=str,
        required=True,
        help="This field cannot be left blank!"
    )
    parser.add_argument('price',
        type=float,
        required=True,
        help="This field cannot be left blank!"
    )
    parser.add_argument('store_id',
        type=int,
        required=True,
        help="Every item need a store id!"
    )

    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

    @jwt_required
    def post(self):
        data = Item.parser.parse_args() 
        if ItemModel.find_by_name(data['name']):
            return {'message': "An item with name '{}' already exists.".format(data['name'])}, 400
        item = ItemModel(**data)
        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred inserting the item."}, 500 
        
        return item.json(), 201

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {'message': 'Item deleted'}

    @jwt_required
    def put(self, name):
        data = Item.parser.parse_args()
        # Once again, print something not in the args to verify everything works

        item = ItemModel.find_by_name(name)

        if item is None: 
            item = ItemModel(name, data['price'], data['store_id'])
        else:
            item.price = data['price']

        item.save_to_db()

        return item.json()


class ItemList(Resource):

    def get(self):
        return {'items': [item.json() for item in ItemModel.find_all()]}, 200


    # return {"items": [item.json() for item in ItemModel.query.all()]}
    # return {"items": list(map(lambda item: item.json, ItemModel.query.all()))}

