import os
basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class BaseConfig(object):
    """Base configuration."""
    # key for jws. It will be used to sign tokens
    # run: export SECRET_KEY = 'asjf safjsfjsalkfjslakjfslakj slkjlks'
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    # for authentication
    # MONGOURL='mongodb://user:password@localhost:27017/?authSource=the_database&authMechanism=SCRAM-SHA-256'
    MONGOURL = os.getenv('MONGOURL', 'mongodb://localhost:27017/')
    MONGODB = 'mytasks'
    DAYS_TO_EXPIRE_TOKEN = 30


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
    """ Warning: this is not a real production config, but a class to TEST
    a production configuration. Use a file config.py for a real configuration
    class """
    DEBUG = False
    SECRET_KEY = "nanana"
