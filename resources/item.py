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

    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)

        if item:
            return item.json()

        return {'message': 'Item not found'}, 404

    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)
        
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
        
        # if ItemModel.find_by_name(name) == None:
        #     return {'message': "An item with name '{}' is not found.".format(name)}, 400

        # connection = sqlite3.connect('data.db')
        # cursor = connection.cursor()

        # query = "DELETE FROM  items WHERE name=?"
        # cursor.execute(query, (name,))

               
        # connection.commit()
        # connection.close()

        # return {'message': 'Item deleted'}

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

    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {'items': items}
        return {
            'items': [item.json() for item in items],
            'message': 'More data available if you log in.'
        }, 200


    # return {"items": [item.json() for item in ItemModel.query.all()]}
    # return {"items": list(map(lambda item: item.json, ItemModel.query.all()))}

#   def get(self):
#         connection = sqlite3.connect('data.db')
#         cursor = connection.cursor()

#         query = "SELECT * FROM items"
#         result = cursor.execute(query)

#         items = []
#         for row in result:
#             items.append({'name': row[0], 'price': row[1]})

#         connection.close()
#         return {"items": items}
