
import os
from flask import Flask
# from flask_pymongo import PyMongo
from mongoengine import connect

from app.config import config
from app.api_v1 import blueprint as apiv0

def establish_db_connection(app):
    db = app.config.get('MONGO_DBNAME', 'ph-dashboard-db')
    host = app.config.get('MONGO_HOST', 'localhost')
    port = app.config.get('MONGO_PORT', 27017)
    username = app.config.get('MONGO_USERNAME', None)
    password = app.config.get('MONGO_PASSWORD', None)
    connect(
        db,
        host=host,
        port=port,
        username=username,
        password=password)

def create_app(config_name):
    '''
    app construction and configuration
    '''
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config.SWAGGER_UI_JSONEDITOR = True
    establish_db_connection(app)
    # db = PyMongo()
    # db.init_app(app)
    app.register_blueprint(apiv0)

    return app
