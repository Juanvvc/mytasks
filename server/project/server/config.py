import os
basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class BaseConfig(object):
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    BASE_URL_API = '/mytasks/api/v1.0'
    MONGOURL = 'mongodb://localhost:27017/'
    MONGODB = 'mytasks'


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    MONGODB = 'mytasks-testing'


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
