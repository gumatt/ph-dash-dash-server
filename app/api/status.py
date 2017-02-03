from flask_restplus import Namespace, Resource
from flask import current_app

API = Namespace('status', description='Application status operations')


@API.route('/')
class Status(Resource):
    """heartbeat monitor of this api"""
    @API.doc('heartbeat')
    def get(self):
        '''simple heartbeat status -
            use to make sure you can reach the server this is a run
            on sentence to see what the swagger api documentation
            looks like with a long doc string
        '''
        return {'status': 'Running in ' + current_app.config['CONFIG']}
