import os
from datetime import timedelta

BASEDIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.environ.get('PH_DASHBOARD_SECRET_KEY') or 'my precious'
JWT_ISSUER = 'ph-dashboard'
JWT_DURATION = timedelta(days=30)


class Config(object):
    SECRET_KEY = SECRET_KEY

    @staticmethod
    def init_app(app):
        pass

class LocalConfig(Config):
    DEBUG = True
    CONFIG = 'local'


class DevelopmentConfig(Config):
    DEBUG = True
    CONFIG = 'development'
    # MONGODB_DB = 'dev_py_proj_db'
    # MONGODB_HOST = 'localhost'
    # MONGODB_PORT = 27017
    # MONGODB_USERNAME = 'gumatt'
    # MONGODB_PASSWORD = ''


class TestingConfig(Config):
    TESTING = True
    CONFIG = 'testing'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
