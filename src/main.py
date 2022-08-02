"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from hmac import compare_digest

from flask import Flask, request, jsonify, url_for, request
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Character, Vehicles, FavoriteVehicles, FavoriteCharacter, FavoritePlanets, Favorites
#from models import Person

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt

app = Flask(__name__, template_folder='./templates')
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

app.config['JWT_SECRET_KEY'] = '4geeks' 
jwt = JWTManager(app)
bcrypt=Bcrypt(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    user = User.query.filter_by(email = email).first()
    if user is None:
        raise APIException("El usuario no existe", status_code=401)
    if password is None:
        raise APIException("Tienes que enviar la constrasena", status_code=404)

    is_correct = bcrypt.check_password_hash(user.password, password)
    if not is_correct:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token= create_access_token(identity=email)
    return jsonify(access_token=access_token), 200


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


##----------------------------------USER CRUD-------------------------------------------------





@app.route("/user", methods=['GET'])
def handle_all_users():
    
    AllUser = User.query.all()
    allUser_serialize = list(map(lambda x:x.serialize(), AllUser ))

    return jsonify(allUser_serialize), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def handle_hello(user_id):
    if user_id == 0:
        raise APIException("No existe el usuario 0", status_code=500)
    user = User.query.get(user_id)

    if user is None:
        raise APIException('El usuario con ese ID no existe', status_code=400)

    response_body = {
        "msg": "Hello, this is your GET /user response, test message ",
        "usuarios": user.serialize()
    }

    return jsonify(response_body), 200

@app.route('/user', methods=['POST'])
def post_new_user():
    body = request.get_json()

    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)

    if 'email' not in body:
        raise APIException("Tienes que agregar el correo del usuario", status_code=400)

    if 'password' not in body:
        raise APIException("Tienes que tener una contraseña. FUERTE.", status_code=404)

    if 'username' not in body:
        raise APIException("Please use a different username", status_code=400)

    useremail = User.query.filter_by(email=body['email']).first()

    if useremail != None:
        raise APIException("El correo ya ha sido registrado anteriormente", status_code=400)

    userUsername = User.query.filter_by(username=body['username']).first()

    if userUsername !=None:
        raise APIException("Este usuario ya ha sido registrado anteriormente", status_code=404)

    pw_hash = bcrypt.generate_password_hash(body['password'])
    new_user = User(email=body['email'], username=body['username'], password=pw_hash, is_active=True)

    db.session.add(new_user)
    db.session.commit()
    response_body = {
        "msg": f"El usuario {new_user.serialize()['username']} ha sido creado."
    }

    return jsonify(response_body), 200

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    body = request.get_json()

    updateUser = User.query.get(body['user_id'])

    if "username" in body:
        updateUser.username = body["username"]
    if "email" in body:
        updateUser.email = body["email"]
    if "name" in body:
        updateUser.name = body["name"]
    if "lastname" in body:
        updateUser.lastname = body["lastname"]
    if "password" in body:
        updateUser.password = body["password"]
    db.session.commit()

    response_body = {
        "message": "ok",
        "updateMsg": "User Updated."
    }

    return jsonify(response_body), 200

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):

    delUser = User.query.get(user_id)

    db.session.delete(delUser)
    db.session.commit()


    response_body = {
        "message": "Ok",
        "deletedUser": "user deleted"
    }

    return jsonify(response_body), 200





##-------------------------------------PLANETS CRUD --------------------------------





@app.route("/planets", methods=['GET'])
def get_all_planets():
    all_planets = Planets.query.all()
    all_planets_serialized = list(map(lambda x:x.serialize(), all_planets))

    response_body = {
        "planets": all_planets_serialized
    }

    return jsonify(response_body), 200

@app.route("/planets/<int:planets_id>", methods=['GET'])
def handle_planet_id(planets_id):

    if planets_id < 1:
        raise APIException("Planet doesn't exist", status_code=404)

    if planets_id == None:
        raise APIException("There is no planet to show", status_code=404)

    planet = Planets.query.get(planets_id)

    response_body = {
        "result": planet.serialize()
    }

    return jsonify(response_body), 200

@app.route('/planets', methods=['POST'])
def post_new_planet():
    body = request.get_json()
    planet = Planets.query.get(planets_id)
    if 'name' not in body:
        raise APIException("Tienes que agregar el nombre del planeta", status_code=400)

    if planets == None:
        raise APIException("This Planet has not been created", status_code=400)

    new_planet = Planets(name=body['name'])

    db.session.add(new_planet)
    db.session.commit()
    response_body = {
        "msg": f"El planeta {new_planet.serialize()['name']} ha sido creado."
    }

    return jsonify(response_body), 200


@app.route("/planets/<int:planets_id>", methods=['PUT'])
def update_planet(planets_id):
    body = request.get_json()

    updatePlanet = Planets.query.get(body['planets_id'])

    if "name" in body:
        updatePlanet.name = body['name']
    if 'diameter' in body:
        updatePlanet.diameter = body['diameter']
    if 'population' in body:
        updatePlanet.population = body['population']
    db.session.commit()

    response_body = {
        "message": "ok",
        "updateMsg": "Planet Updated."
    }

@app.route("/planets/<int:planets_id>", methods=['DELETE'])
def delete_planet_id(planets_id):

    planet = Planets.query.get(planets_id)

    db.session.delete(planet)
    db.session.commit()

    response_body = {
        "message": "Ok",
        "deletedPlanet": "planet deleted"
    }

    return jsonify(planet), 200




##------------------------------------CHARCTER CRUD -----------------------------




@app.route("/character", methods=['GET'])
def get_all_character():
    all_character = Character.query.all()
    all_character_serialized = list(map(lambda x:x.serialize(), all_character))

    response_body = {
        "character": all_character_serialized
    }

    return jsonify(response_body), 200


@app.route("/character/<int:character_id>", methods=['GET'])
def handle_character_id(character_id):

    if character_id < 1:
        raise APIException("Character doesn't exist", status_code=404)

    if character_id == None:
        raise APIException("There is no character to show", status_code=404)

    character = Character.query.get(character_id)

    response_body = {
        "result": character.serialize()
    }

    return jsonify(response_body), 200

@app.route('/character', methods=['POST'])
def post_new_character():
    body = request.get_json()
    character = Character.query.get(character_id)

    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)

    if 'name' not in body:
        raise APIException("Tienes que agregar el nombre del personaje", status_code=400)

    if 'last_name' not in body:
        raise APIException("Tienes que agregar el apellido del personaje", status_code=400)

    if character == None:
        raise APIException("This Character has not been created", status_code=400)

    new_character = Character(name=body['name'], last_name=body['last_name'])

    db.session.add(new_character)
    db.session.commit()
    response_body = {
        "msg": f"El personaje {new_character.serialize()['name']} ha sido creado."
    }

    return jsonify(response_body), 200


@app.route("/character/<int:characters_id>", methods=['PUT'])
def update_character(character_id):
    body = request.get_json()

    updateCharacter = Vehicles.query.get(planets_id)

    if "name" in body:
        updateCharacter.name = body['name']
    if 'last_name' in body:
        updateCharacter.last_name = body['last_name']
    if 'height' in body:
        updateCharacter.height = body['height']
    if 'hair_color' in body:
        updateCharacter.hair_color = body['hair_color']
    if 'birth_year' in body:
        updateCharacter.birth_year = body['birth_year']
    db.session.commit()

    response_body = {
        "message": "ok",
        "updateMsg": "Character Updated."
    }

@app.route("/characters/<int:characters_id>", methods=['DELETE'])
def delete_character_id(character_id):

    character = Character.query.get(character_id)

    db.session.delete(character)
    db.session.commit()

    response_body = {
        "message": "Ok",
        "deletedCharacter": "character deleted"
    }

    return jsonify(character), 200






##----------------------------------VEHICLE CRUD ------------------------------






@app.route("/vehicles", methods=['GET'])
def get_all_vehicles():
    all_vehicles = Vehicles.query.all()
    all_vehicles_serialized = list(map(lambda x:x.serialize(), all_vehicles))

    response_body = {
        "vehicles": all_vehicles_serialized
    }

    return jsonify(response_body), 200

@app.route("/vehicles/<int:vehicles_id>", methods=['GET'])
def handle_vehicles_id(vehicles_id):

    if vehicles_id < 1:
        raise APIException("Vehicle doesn't exist", status_code=404)

    if vehicles_id == None:
        raise APIException("There are no vehicles to show", status_code=404)

    vehicles = Vehicles.query.get(vehicles_id)

    response_body = {
        "result": vehicles.serialize()
    }

    return jsonify(response_body), 200

@app.route('/vehicles', methods=['POST'])
def post_new_vehicle():
    body = request.get_json()
    vehicle = Character.query.get(vehicle_id)


    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)

    if 'name' not in body:
        raise APIException("Tienes que agregar el nombre del vehiculo", status_code=400)

    if vehicle == None:
        raise APIException("This Vehicle has not been created", status_code=400)

    new_vehicle = Vehicles(name=body['name'], last_name=body['last_name'])

    db.session.add( new_vehicle)
    db.session.commit()
    response_body = {
        "msg": f"El vehiculo { new_vehicle.serialize()['name']} ha sido creado."
    }

    return jsonify(response_body), 200


@app.route("/vehicles/<int:vehicles_id>", methods=['PUT'])
def update_vehicle(vehicles_id):
    body = request.get_json()

    updateVehicle = Vehicles.query.get(vehicles_id)
    
    if "name" in body:
        updateVehicle.name = body['name']
    if 'model' in body:
        updateVehicle.model = body['model']
    if 'cost_in_credits' in body:
        updateVehicle.cost_in_credits = body['cost_in_credits']
    db.session.commit()

    response_body = {
        "message": "ok",
        "updateMsg": "Vehicle Updated."
    }

    return jsonify(response_body), 200

@app.route("/vehicles/<int:vehicles_id>", methods=['DELETE'])
def delete_vehicles_id(vehicles_id):

    vehicle = Vehicles.query.get(vehicles_id)

    db.session.delete(vehicle)
    db.session.commit()

    response_body = {
        "message": "Ok",
        "deletedVehicle": "vehicle deleted"
    }

    return jsonify(vehicle), 200






##-------------------------------FAVORITE CHARACTER -------------------------







@app.route("/favoritecharacter", methods=['GET'])
@jwt_required()
def get_all_favcharacters():
    all_favchar = FavoriteCharacter.query.all()
    all_favchar_serialized = list(map(lambda x:x.serialize(), all_favchar))

    response_body = {
        "favoritecharacters": all_favchar_serialized
    }

    return jsonify(response_body), 200

@app.route("/favoritecharacter/<int:favoritecharacter_id>", methods=['GET'])
@jwt_required()
def handle_favchar_id(favoritecharacter_id):

    if favoritecharacter_id < 1:
        raise APIException("This character does not exist on your favorites", status_code=404)

    if favoritecharacter_id == None:
        raise APIException("There is no favorite character to show", status_code=404)

    favchar = FavoriteCharacter.query.get()

    response_body = {
        "result": favchar.serialize()
    }

    return jsonify(response_body), 200

@app.route("/users/favorites/character", methods=['POST'])
def post_favoritecharacter():
    body = request.get_json()
    
    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)

    postUserId = User.query.get(body['user_id'])
    if postUserId == None:
        raise APIException("This character does not exist...yet", status_code=404)

    registerExist = FavoriteCharacter.query.filter_by(character_id = body['character_id']).filter_by(user_id = body['user_id']).all()

    if len(registerExist) > 0:
        raise APIException("This character already has this favorite character.", status_code=404)

    postCharacterId = Character.query.get(body['character_id'])
    if postCharacterId == None:
        raise APIException("This character is not on the list...yet", status_code=404)

    postfavcharacter = FavoriteCharacter(character_id = body['character_id'], user_id = body['user_id'])
    db.session.add(postfavcharacter)
    db.session.commit()

    response_body = {
        "message": postfavcharacter.serialize()
    }

    return jsonify(response_body), 200


@app.route("/favoritecharacter/<int:favoritecharacter_id>", methods=['DELETE'])
def delete_favchar_id(favoritecharacter_id):

    favcharacters = FavoriteCharacter.query.get(favoritecharacter_id)

    db.session.delete(favcharacters)
    db.session.commit()

    response_body = {
        "message": "Ok",
        "deletedFavCharacter": "Favorite character deleted"
    }

    return jsonify(favcharacters), 200






##-------------------------------FAVORITE VEHICLES -------------------------







@app.route("/favoritevehicles", methods=['GET'])
@jwt_required()
def get_all_favvehicles():
    all_favveh = FavoriteVehicles.query.all()
    all_favveh_serialized = list(map(lambda x:x.serialize(), all_favveh))

    response_body = {
        "favoritevehicles": all_favveh_serialized
    }

    return jsonify(response_body), 200


@app.route("/favoritevehicles/<int:favoritevehicles_id>", methods=['GET'])
@jwt_required()
def handle_favvehicles_id(favoritevehicles_id):

    if favoritevehicles_id < 1:
        raise APIException("This vehicle does not exist on your favorites", status_code=404)

    if favoritevehicles_id == None:
        raise APIException("There is no favorite vehicle to show", status_code=404)

    favveh = FavoriteVehicles.query.get()

    response_body = {
        "result": favveh.serialize()
    }

    return jsonify(response_body), 200

@app.route("/users/favorites/vehicle", methods=['POST'])
def post_favoriteVehicle():
    body = request.get_json()
    
    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)

    postUserId = User.query.get(body['user_id'])
    if postUserId == None:
        raise APIException("This user does not exist...yet", status_code=404)

    registerExist = FavoriteVehicles.query.filter_by(vehicles_id = body['vehicles_id']).filter_by(user_id = body['user_id']).all()

    if len(registerExist) > 0:
        raise APIException("This user already has this favorite vehicle.", status_code=404)

    postVehicle = Vehicles.query.get(body['vehicles_id'])
    if postPlanets == None:
        raise APIException("This vehicle is not on the list...yet", status_code=404)

    postfavvehicle = FavoriteVehicles(vehicles_id = body['vehicles_id'], user_id = body['user_id'])
    db.session.add(postfavvehicle)
    db.session.commit()

    response_body = {
        "message": postfavvehicle.serialize()
    }

    return jsonify(response_body), 200



@app.route("/favoritevehicles/<int:favoritevehicles_id>", methods=['DELETE'])
def delete_favvehicles_id(favoritevehicles_id):

    favvehicle = FavoriteVehicles.query.get(favoritevehicles_id)

    db.session.delete(favvehicle)
    db.session.commit()

    response_body = {
        "message": "Ok",
        "deletedFavVehicle": "Favorite vehicle deleted"
    }

    return jsonify(favvehicle), 200







##-------------------------------FAVORITE PLANETS-------------------------







@app.route("/favoriteplanets", methods=['GET'])
@jwt_required()
def get_all_favplanets():
    all_favplan = FavoritePlanets.query.all()
    all_favplan_serialized = list(map(lambda x:x.serialize(), all_favplan))

    response_body = {
        "favoriteplanets": all_favplan_serialized
    }

    return jsonify(response_body), 200

@app.route("/favoriteplanets/<int:favoriteplanets_id>", methods=['GET'])
@jwt_required()
def handle_favplanets_id(favoriteplanets_id):
    if favoriteplanets_id <1:
        raise APIException("This planet doesn't not exist on your favorites.", status_code = 404)

    if favoriteplanets_id == None:
        raise APIException("There is no favorite vehicle to show", status_code = 404)

    favplan = FavoritePlanets.query.get()

    response_body = {
        "result": favplan.serialize()
    }

    return jsonify(response_body), 200

@app.route("/users/favorites/planets", methods=['POST'])
def post_favoritePlanets():
    body = request.get_json()

    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)
    
    postUserId = User.query.get(body['user_id'])
    if postUserId == None:
        raise APIException("This user does not exist...yet", status_code=404)

    registerExist = FavoritePlanets.query.filter_by(planets_id = body['planets_id']).filter_by(user_id = body['user_id']).all()

    if len(registerExist) > 0:
        raise APIException("This planet already has this favorite planets.", status_code=404)

    postPlanets = Planets.query.get(body['planets_id'])
    if postPlanets == None:
        raise APIException("This planet is not on the list...yet", status_code=404)

    postfavplanets = FavoritePlanets(planets_id = body['planets_id'], user_id = body['user_id'])
    db.session.add(postfavplanets)
    db.session.commit()

    response_body = {
        "message": postfavplanets.serialize()
    }

    return jsonify(response_body), 200


@app.route("/favoriteplanets/<int:favoriteplanets_id>", methods=['DELETE'])
def delete_favplanets_id(favoriteplanets_id):

    favplanets = FavoritePlanets.query.get(favoriteplanets_id)
    
    db.session.delete(favplanets)
    db.session.commit()

    response_body = {
        "message": "Ok",
        "deletedFavCharacter": "Favorite planet deleted"
    }

    return jsonify(favplanets), 200





##----------------------------------Favorites --------------------





@app.route("/users/favorites", methods=['GET'])
@jwt_required()
def get_favorites():
    all_favorites = Favorites.query.all()
    all_favorites_serialized = list(map(lambda x:x.serialize(), all_favorites))

    response_body = {
        "favorites": all_favorites_serialized
    }

    return jsonify(response_body), 200



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

