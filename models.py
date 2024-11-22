from database import db

from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import JSONB


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attributes = db.Column(db.JSON, nullable=False) 
    group_id = db.Column(db.Integer, db.ForeignKey('group.id')) 


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attributes = db.Column(JSONB, nullable=False)  

