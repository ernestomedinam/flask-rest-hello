from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(40), nullable=False) 
    members = db.relationship("FamilyBond", backref="family")
    
    def __init__(self, last_name):
        self.last_name = last_name
        db.session.add(self)
        try: 
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise Exception(error.args)
    
    def serialize(self):
        bond_dictionaries = []
        for bond in self.members:
            bond_dictionaries.append(
                bond.serialize()
            )
        return {
            "id": self.id,
            "last_name": self.last_name,
            "members": bond_dictionaries
        }
    
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40), nullable=False) 
    age = db.Column(db.Integer)
    led_family_id = db.Column(db.Integer, db.ForeignKey("family.id"))
    bonds = db.relationship("FamilyBond", backref="member")

    def __init__(self, first_name, age):
        self.first_name = first_name
        self.age = age
        self.led_family_id = None
        db.session.add(self)
        db.session.commit()
    
    def serialize(self): 
        return {
            "id": self.id,
            "first_name": self.first_name,
            "age": self.age,
            "led_family_id": self.led_family_id
        }

class FamilyBond(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    member_id = db.Column(db.Integer, db.ForeignKey("member.id"))
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"))

    def __init__(self, member_id, family_id):
        self.member_id = member_id
        self.family_id = family_id
        db.session.add(self)
        db.session.commit()
    
    def serialize(self):
        return {
            **self.member.serialize()
        }