#!/usr/bin/env python3

from flask import Flask, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound

from models import db, Hero,Power,HeroPower


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)
# create a response for landing page

class Home(Resource):
    def get(self):
        response_message = {
            "message": "WELCOME TO THE PIZZA RESTAURANT API."
        }
        return make_response(response_message, 200)


api.add_resource(Home, '/')

class Heroes(Resource):
# get all restaurants 
    def get(self):
        heroes = []
        for hero  in Hero.query.all():
            hero_dict={
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name,
            }
            heroes.append(hero_dict)
        return make_response(jsonify(heroes), 200)

    

api.add_resource(Heroes, '/heroes')

# deals with restaurant routes
class HeroByID(Resource):
# get restaurants by id 
    def get(self, id):
        hero = Hero.query.filter_by(id=id).first()
        if hero:
            hero_dict={
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name,
                "powers":[
                    {
                        "id": hero_power.power.id,
                        "name": hero_power.power.name,
                        "description": hero_power.power.description,
                    }
                    for hero_power in hero.powers
                ]
            }
            return make_response(jsonify(hero_dict), 200)
        else:
            return make_response(jsonify({"error": "Hero not found"}), 404)




api.add_resource(HeroByID, '/heroes/<int:id>')

class PowerByID(Resource):
# get restaurants by id 
    def get(self, id):
        power = Power.query.filter_by(id=id).first()
        if power:
            power_dict={
                "id": power.id,
                "name": power.name,
                "description": power.description,
                
            }
            return make_response(jsonify(power_dict), 200)
        else:
            return make_response(jsonify({"error": "Power not found"}), 404)
        
    def patch(self,id):
        power = Power.query.filter_by(id=id).first()
        data = request.get_json()
        if power:
            for attr in data:
                   setattr(power, attr, data[attr])
            
            db.session.add(power)
            db.session.commit()
            power_dict={
                "id": power.id,
                "name": power.name,
                "description": power.description,
                
            }
            return make_response(power_dict, 200)
        else:
            return make_response(jsonify({"error": "Power not found"}), 404)

api.add_resource(PowerByID, '/powers/<int:id>')
class HeroPowers(Resource):
    def post(self):
        data = request.get_json()

       # Validate that the required fields are present in the request
        required_fields = ["strength", "power_id", "hero_id"]
        if not all(key in data for key in required_fields):
            return make_response(jsonify({"errors": ["Validation errors"]}), 400)

        # Check if the Hero and Power exist
        hero = Hero.query.get(data['hero_id'])
        power = Power.query.get(data['power_id'])

        if not hero or not power:
            return make_response(jsonify({"errors": ["Validation errors"]}), 400)

        # Create a new HeroPower
        hero_power = HeroPower(
            strength=data["strength"],
            hero_id=data["hero_id"],
            power_id=data["power_id"]
        )

        db.session.add(hero_power)
        db.session.commit()

        hero_data={
               "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name,
                "powers":[
                    {
                        "id": hero_power.power.id,
                        "name": hero_power.power.name,
                        "description": hero_power.power.description,
                    }
                    for hero_power in hero.powers
                ]
            
        }
        return make_response(jsonify(hero_data), 201)

api.add_resource(HeroPowers,'/hero_powers')   

if __name__ == '__main__':
    app.run(port=5555, debug=True)

