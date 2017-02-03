
import os
from flask import Flask

from app.config import config
from app.api_v1 import blueprint as apiv0

def create_app(config_name):
    '''
    app construction and configuration
    '''
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config.SWAGGER_UI_JSONEDITOR = True
    app.register_blueprint(apiv0)

    return app
