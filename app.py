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

def assign_group(user_id, attributes):
    group = Group.query.filter_by(attributes=attributes).first()
    if not group:
        group = Group(attributes=attributes)
        db.session.add(group)
        db.session.commit()
    
    user = User.query.get(user_id)
    user.group_id = group.id
    db.session.commit()

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

    group_id = user.group_id
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'error': 'Group not found'}), 404

    group_data = GroupSchema().dump(group)
    return jsonify(group_data)

if __name__ == '__main__':
    app.run(debug=True)
