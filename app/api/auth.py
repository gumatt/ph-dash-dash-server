from flask import request
from flask_restplus import Namespace, Resource, fields, abort

from app.models import User
from app.config import SECRET_KEY, JWT_ISSUER, JWT_DURATION

API = Namespace('auth', description='Application authentication and access control')

LOGIN_MODEL = API.model('auth', {
    'username': fields.String(
        required=True,
        description='unique short username',
        example='gumatt, peter01, HappyGuy23'),
    'password': fields.String(
        required=True,
        description='password of less than 25 characters')
})

REGISTERATION_MODEL = LOGIN_MODEL.clone('registeration', {
    'email': fields.String(
        description='user email address',
        example='test@test.com')
})

API.models[REGISTERATION_MODEL.name] = REGISTERATION_MODEL

E400_INVALID_USERNAME_PASSWORD = 'invalid username and/or password'
E409_USERNAME_EXISTS = 'username already registered'

def is_valid_password(password):
    return password

@API.route('/register')
class Registeration(Resource):

    @API.response(200, 'Success')
    @API.response(400, E400_INVALID_USERNAME_PASSWORD)
    @API.response(409, E409_USERNAME_EXISTS)
    @API.expect(REGISTERATION_MODEL)
    def post(self):
        ''' register username and password, and (optionally) an emailaddress
        '''
        args = request.get_json()
        username = args.get('username')
        if username and User.objects(username=username).count() > 0:
            abort(409, E409_USERNAME_EXISTS)
        password = args.get('password')
        email = args.get('email', None)
        User(username=username, password=password, email=email).save()

        return {'token': 'token logic coming'}
