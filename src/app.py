"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Family, FamilyBond, Member
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/families', methods=['GET', 'POST'])
def handle_families():
    if request.method == "POST":
        last_name = request.json["last_name"]
        new_family = Family(
            last_name=last_name
        )
        return jsonify(new_family.serialize()), 201
    families = Family.query.all()
    family_dictionaries = []
    for family in families:
        family_dictionaries.append(
            family.serialize()
        )
    return jsonify(family_dictionaries), 200

@app.route("/members", methods=["POST"])
def handle_members():
    body = request.json
    family = Family.query.get(body["family_id"])
    if family is None:
        return jsonify({
            "msg": "no such family 😐"
        }), 404
    new_member = Member(
        first_name=body["first_name"],
        age=body["age"]
    )
    new_bond = FamilyBond(
        member_id=new_member.id,
        family_id=family.id
    )
    return jsonify(new_member.serialize()), 201

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
