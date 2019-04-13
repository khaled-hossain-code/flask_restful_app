from flask import Flask, request
from flask_restful import Resource, Api, abort
from flask_jwt import JWT, jwt_required

from security import authenticate, identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
api = Api(app)

jwt = JWT(app, authenticate, identity)  # /auth

items = []


def find_or_abort(item_name):
    for item in items:
        if item['name'] == item_name:
            return item

    abort(404, message="Item {} doesn't exist".format(item_name))


def get_item(item_name):
    return next(filter(lambda item: item['name'] == item_name, items), None)


class ItemList(Resource):
    @jwt_required()
    def get(self):
        return items

    def post(self):
        data = request.get_json()
        if get_item(data['name']):
            return {'message': "An item with name '{}' already exists.".format(data['name'])}, 400

        items.append(data)
        return data, 201


api.add_resource(ItemList, '/items')


class Item(Resource):
    def get(self, item_name):
        item = find_or_abort(item_name)
        return item, 200

    def put(self, item_name):
        data = request.get_json()
        item = find_or_abort(item_name)
        item['price'] = data['price']
        return item

    def delete(self, item_name):
        delete_item = find_or_abort(item_name)
        items[:] = [item for item in items if item['name'] != delete_item['name']]
        return items


api.add_resource(Item, '/items/<item_name>')

app.run(port=5500, debug=True)
