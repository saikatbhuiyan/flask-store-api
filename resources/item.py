import sqlite3
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required, current_identity

from security import authenticate, identity
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help="This field cannot be left blank!"
    )

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)

        if item:
            return item

        return {'message': 'Item not found'} 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400

        data = Item.parser.parse_args()

        item = {'name': name, 'price': data['price']}
        
        try:
            ItemModel.insert(item)
        except:
            return {"message": "An error occurred inserting the item."}, 500 
        
        return item, 201

    @jwt_required()
    def delete(self, name):
        if ItemModel.find_by_name(name) == None:
            return {'message': "An item with name '{}' is not found.".format(name)}, 400

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM  items WHERE name=?"
        cursor.execute(query, (name,))

               
        connection.commit()
        connection.close()

        return {'message': 'Item deleted'}

    @jwt_required()
    def put(self, name):
        data = Item.parser.parse_args()
        # Once again, print something not in the args to verify everything works

        item = ItemModel.find_by_name(name)
        update_item = {'name': name, 'price': data['price']}
        if item is None: 
            try:
                ItemModel.insert(update_item)
            except:
                return {"message": "An error occurred inserting the item."}, 500 
  
        else:
            try:
                ItemModel.update(update_item)
            except:
                return {"message": "An error occurred updating the item."}, 500 
  
        return item


class ItemList(Resource):

  def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items"
        result = cursor.execute(query)

        items = []
        for row in result:
            items.append({'name': row[0], 'price': row[1]})

        connection.close()
        return {"items": items}