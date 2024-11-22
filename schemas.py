from flask_marshmallow import Marshmallow 
ma = Marshmallow()

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'attributes', 'group_id')

class GroupSchema(ma.Schema):
    class Meta:
        fields = ('id', 'attributes', 'users')
