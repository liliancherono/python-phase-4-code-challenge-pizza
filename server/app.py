#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os
from flask import jsonify

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# create tables if they don't exist (helps tests)
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route('/restaurants')
def restaurants_index():
    restaurants = Restaurant.query.all()
    data = [r.to_dict(only=('id','name','address')) for r in restaurants]
    return make_response(jsonify(data), 200)


@app.route('/restaurants/<int:id>')
def restaurants_show(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return make_response(jsonify({'error': 'Restaurant not found'}), 404)
    data = restaurant.to_dict()
    return make_response(jsonify(data), 200)


@app.route('/restaurants/<int:id>', methods=['DELETE'])
def restaurants_delete(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return make_response(jsonify({'error': 'Restaurant not found'}), 404)
    db.session.delete(restaurant)
    db.session.commit()
    return make_response('', 204)


@app.route('/pizzas')
def pizzas_index():
    pizzas = Pizza.query.all()
    data = [p.to_dict(only=('id','name','ingredients')) for p in pizzas]
    return make_response(jsonify(data), 200)


@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    try:
        rp = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(rp)
        db.session.commit()
    except ValueError:
        db.session.rollback()
        return make_response(jsonify({'errors': ['validation errors']}), 400)
    except Exception:
        db.session.rollback()
        return make_response(jsonify({'errors': ['validation errors']}), 400)

    return make_response(jsonify(rp.to_dict()), 201)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
