from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    name = db.Column(db.String(120), unique=False, nullable=True)
    lastname = db.Column(db.String(120), unique=False, nullable=True)

    def __repr__(self):
        return f'El usuario con email: {self.email}'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
            # do not serialize the password, its a security breach
        }

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    population = db.Column(db.Integer, nullable=True)
    diameter = db.Column(db.Integer, nullable=True)


    def __repr__(self):
        return f"Planeta {self.name} con ID {self.id}. Su diametro es de {self.diameter} y tiene una poblacion de {self.population}. "

    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'population' : self.population,
            'diameter': self.diameter
        }

class Vehicles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    model = db.Column(db.String(120), nullable=True)
    cost_in_credits = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"{self.name} con ID {self.id} tiene un costo de {self.cost_in_credits}"

    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'model' : self.model,
            'cost_in_credits' : self.cost_in_credits
        }

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    last_name = db.Column(db.String(120), unique=False, nullable=False)
    height = db.Column(db.Integer, nullable=True)
    hair_color = db.Column(db.String(120), nullable=True)
    birth_year = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"{self.name} {self.last_name} con ID {self.id}"

    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'last_name' : self.last_name,
            'hair_color' : self.hair_color,
            'birth_year' : self.birth_year
        }

class FavoriteCharacter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id', ondelete='CASCADE'))
    character = db.relationship(Character, primaryjoin=character_id == Character.id)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    User = db.relationship('User', primaryjoin=user_id == User.id)

    def __repr__(self):
        return '<FavoriteCharacter %r' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'character_id': self.character_id,
            'user_id': self.user_id 
        }

class FavoriteVehicles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicles_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'))
    vehicles = db.relationship(Vehicles, primaryjoin=vehicles_id == Vehicles.id)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    User = db.relationship('User', primaryjoin=user_id == User.id)

    def __repr__(self):
        return '<FavoriteVehicle %r' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'user_id': self.user_id
        }

class FavoritePlanets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planets_id = db.Column(db.Integer, db.ForeignKey('planets.id', ondelete='CASCADE'))
    planets = db.relationship(Planets, primaryjoin=planets_id == Planets.id)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    User = db.relationship('User', primaryjoin=user_id == User.id)
    
    def __repr__(self):
        return '<FavoritePlanets %r' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'planets_id': self.planets_id,
            'user_id': self.user_id
        }


class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id', ondelete='CASCADE'))
    character = db.relationship(Character, primaryjoin=character_id == Character.id)
    vehicles_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'))
    vehicles = db.relationship(Vehicles, primaryjoin=vehicles_id == Vehicles.id)
    planets_id = db.Column(db.Integer, db.ForeignKey('planets.id', ondelete='CASCADE'))
    planets = db.relationship(Planets, primaryjoin=planets_id == Planets.id)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    User = db.relationship('User', primaryjoin=user_id == User.id)

    def __repr__(self):
        return '<Favorites %r' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'planets_id': self.planets_id,
            'character_id': self.character_id,
            'vehicle_id': self.vehicles_id,
            'user_id': self.user_id
        }