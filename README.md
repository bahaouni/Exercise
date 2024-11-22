Project Overview
This Flask application implements a social network where users are automatically grouped based on their attributes. Users specify a set of attributes when joining the app, and the system groups them with others who share a subset of those attributes, according to a configurable matching threshold.

If no existing group satisfies the matching criteria, a new group is created. The application supports:

Automatic user grouping.
JWT-based authentication for secure endpoints.
Viewing group members.
Key Components
1. Flask Application Structure
The project structure includes:

Models (models.py): Defines the database models for User and Group.
Schemas (schemas.py): Provides serialization/deserialization of data for API endpoints using Marshmallow.
Database (database.py): Sets up the SQLAlchemy integration for PostgreSQL.
Configuration (config.py): Centralized configuration settings for the app.
Application Logic (app.py): Contains routes for user signup, authentication, and group retrieval.
2. Key Functionalities
User Signup
Endpoint: /signup
Method: POST
Description:
Adds a new user to the database.
Automatically assigns the user to an existing group or creates a new group if no suitable match is found.
User Signin
Endpoint: /signin
Method: POST
Description:
Authenticates the user by generating a JWT token.
Retrieve Group Members
Endpoint: /groups/<int:user_id>
Method: GET
Description:
Retrieves the group and its members for a given user ID.
Requires JWT authentication.
How the Grouping Works
Grouping Logic
The assign_group function ensures that users are grouped effectively:

Checks all existing groups using the group_map (an in-memory dictionary for performance).
Calculates the intersection of attributes between the user and each group.
Selects the group with the most matching attributes (at least minimum_matching_threshold attributes).
If no group satisfies the threshold, a new group is created, and the user is assigned to it.
Code Breakdown
Models
python
Copy code
from database import db
from sqlalchemy.dialects.postgresql import JSON, JSONB

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attributes = db.Column(db.JSON, nullable=False)  # Stores user attributes as JSON
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))  # Links user to a group

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attributes = db.Column(JSONB, nullable=False)  # Stores group attributes as JSONB
Schemas
python
Copy code
from flask_marshmallow import Marshmallow

ma = Marshmallow()

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'attributes', 'group_id')  # Fields exposed in the API

class GroupSchema(ma.Schema):
    class Meta:
        fields = ('id', 'attributes', 'users')  # Fields exposed in the API
Database Setup
python
Copy code
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
Application Configuration
python
Copy code
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mysecret")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost/assignment"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwtsecret")
Grouping Logic
python
Copy code
from models import User, Group
from database import db

group_map = {}  # In-memory data structure: {group_id: set(attributes)}

def initialize_group_map():
    """
    Populate the in-memory group_map from the database.
    """
    global group_map
    group_map = {group.id: set(group.attributes) for group in Group.query.all()}

def assign_group(user_id, attributes, minimum_matching_threshold=3):
    """
    Assign a user to a group based on attribute matching. Create a new group if no match.
    """
    global group_map
    user_attributes_set = set(attributes)
    best_group = None
    max_matching_attributes = 0

    for group_id, group_attributes_set in group_map.items():
        matching_attributes = user_attributes_set & group_attributes_set
        match_count = len(matching_attributes)

        if match_count > max_matching_attributes and match_count >= minimum_matching_threshold:
            max_matching_attributes = match_count
            best_group = group_id

    if best_group:
        group_id = best_group
    else:
        new_group = Group(attributes=attributes)
        db.session.add(new_group)
        db.session.commit()
        group_map[new_group.id] = user_attributes_set
        group_id = new_group.id

    user = User.query.get(user_id)
    user.group_id = group_id
    db.session.commit()

    return group_id
Routes
python
Copy code
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_migrate import Migrate
from database import db
from models import User, Group
from schemas import UserSchema, GroupSchema

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    attributes = data.get('attributes', [])
    user = User(attributes=attributes)
    db.session.add(user)
    db.session.commit()

    assign_group(user.id, attributes)
    return UserSchema().jsonify(user), 201

@app.route('/signin', methods=['POST'])
def signin():
    user_id = request.json.get('user_id')
    token = create_access_token(identity=user_id)
    return jsonify({'token': token})

@app.route('/groups/<int:user_id>', methods=['GET'])
@jwt_required()
def get_groups(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    group = Group.query.get(user.group_id)
    if not group:
        return jsonify({'error': 'Group not found'}), 404

    group_data = GroupSchema().dump(group)
    return jsonify(group_data)

if __name__ == '__main__':
    app.run(debug=True)
Testing
1. Signup
bash
Copy code
curl -X POST http://127.0.0.1:5000/signup -H "Content-Type: application/json" -d '{
    "attributes": ["Software", "Engineer", "Senior", "Brussels"]
}'
2. Signin
bash
Copy code
curl -X POST http://127.0.0.1:5000/signin -H "Content-Type: application/json" -d '{
    "user_id": 1
}'
3. Get Group
bash
Copy code
curl -X GET http://127.0.0.1:5000/groups/1 -H "Authorization: Bearer <JWT_TOKEN>"
Deployment Notes
Ensure PostgreSQL is running and properly configured in config.py.
Use flask db init, flask db migrate, and flask db upgrade to set up the database.
Summary
This documentation covers all major components of the app, including how users are grouped, how routes function, and how to test and deploy the application. Let me know if you need further clarifications!
