from flask import Blueprint
from flask_restplus import Api

from .api.status import API as status

blueprint = Blueprint('api', __name__, url_prefix='/api/v0')
api = Api(
    blueprint,
    title='Gumatt App API Playground',
    version='1.0',
    description='A playground for learning flaskplus library and API design'
    )

api.add_namespace(status)
