from flask import request
from flask_restplus import Namespace, Resource, fields, abort

from app.models import Call

API = Namespace('calls', description='Call data retrieval and actions')

@API.route('/esi_update')
class Registeration(Resource):

    @API.response(200, 'Success')
    def post(self):
        ''' pull data from ESI for calls from 'from_date' to 'to_date'
        '''
        args = request.get_json()
        from_date = args.get('from_date')
        to_date = args.get('to_date')
        if not from_date or not is_valid_date(from_date):
            abort(409, E409_BAD_DATE_FORMAT)
        if to_date and not is_valid_date(to_date):
            abort(409, E409_BAD_DATE_FORMAT)
        # esi.update_data_request(from_date, to_date)


        return {'service_response': 'request has been submitted'}

