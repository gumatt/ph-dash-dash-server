import os
from datetime import timedelta

BASEDIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.environ.get('PH_DASHBOARD_SECRET_KEY') or 'my precious'
JWT_ISSUER = 'ph-dashboard'
JWT_DURATION = timedelta(days=30)


class Config(object):
    SECRET_KEY = SECRET_KEY
    MONGO_DBNAME = 'ph-dashboard-db'

    @staticmethod
    def init_app(app):
        pass

class LocalConfig(Config):
    DEBUG = True
    CONFIG = 'local'


class StageConfig(Config):
    DEBUG = True
    CONFIG = 'development'
    # MONGO_URI = mongodb://<dbuser>:<dbpassword>@ds139909.mlab.com:39909/ph-dashboard-db
    MONGO_HOST = 'ds139909.mlab.com'
    MONGO_PORT = 39909
    MONGO_USERNAME = os.environ.get('MONGO_USERNAME', None)
    MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', None)


class TestingConfig(Config):
    TESTING = True
    CONFIG = 'testing'


config = {
    'stage': StageConfig,
    'testing': TestingConfig,
    'default': LocalConfig
}
