from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
from flask_cors import CORS
import json
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, check_permissions, requires_auth, verify_decode_jwt

app = Flask(__name__)
setup_db(app)
CORS(app)

#auth0 authorize link: https://udacity-coffee-shop-2021.us.auth0.com/authorize?audience=drinks&response_type=token&client_id=vU69Bp38KvkhmoPn833Dz1woaGjOjxaW&redirect_uri=http://localhost:8100

db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    print(repr(drinks))
    return jsonify({
        "success":True,
        "drinks":[repr(drinks)]
    })

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    return jsonify({
        "success":True,
        "drinks":[drink.long() for drink in drinks]
    })

@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    try:
        body = request.get_json()
        print(json.dumps(body['recipe']))
        drink = Drink(title=body['title'],recipe=json.dumps(body['recipe']))
        drink.insert()
        return jsonify({
            "success":True,
            "drinks":[drink.long()]
        })
    except:
        abort(422)

@app.route('/drinks/<drink_id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt,drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    body = request.get_json()
    if 'title' in body:
        drink.title = body['title'] 
    if 'recipe' in body:
        drink.recipe = json.dumps(body['recipe']) 
    drink.update()
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })

@app.route('/drinks/<drink_id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(rwt,drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    drink.delete()
    return jsonify({
        'success': True,
        'delete': drink_id
    })

# Error Handling
# @app.errorhandler(404)
# def not_found(error):
#     return jsonify({
#         "success": False,
#         "error": 404,
#         "message": "resource not found"
#     }), 4

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
