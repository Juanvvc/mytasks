import flask
from flask_httpauth import HTTPBasicAuth
from project.model import search_username
import datetime
import jwt
from bson.objectid import ObjectId
from bson.errors import InvalidId


def create_auth():
    auth = HTTPBasicAuth()

    @auth.verify_password
    def verify_password(username, password):
        if not password:
            # no password: assume there is a token in the username
            flask.current_app.logger.info('Verifying token')
            user = decode_auth_token(username)
            if user is not None and type(user) == ObjectId:
                flask.g.user_id = str(user)
                flask.current_app.logger.info('Token for user %s', str(user))
                return True
            flask.current_app.logger.warning('Token not valid')
            return False

        # there is a password: assume it is a user/password pair
        flask.current_app.logger.info('Verifying password for user %s', username)
        user = search_username(username)
        if not user or not user.verify_password(password):
            flask.current_app.logger.warning('Password not valid for username: %s', username)
            return False
        flask.g.user_id = str(user.id())
        return True

    @auth.error_handler
    def auth_error():
        return flask.make_response(flask.jsonify(dict(error_message='Unauthorized', status=401)))

    return auth


def encode_auth_token(user_id):
    """
    Generates the Auth Token

    Return:
        string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=60),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            flask.current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e


def decode_auth_token(auth_token):
    """
    Decodes the auth token

    Attrs:
        auth_token:

    Return:
        integer|string
    """
    try:
        payload = jwt.decode(auth_token, flask.current_app.config.get('SECRET_KEY'))
        return ObjectId(payload.get('sub', ''))
    except jwt.ExpiredSignatureError:
        flask.current_app.logger.debug('Expired token')
        return None
    except jwt.InvalidTokenError:
        flask.current_app.logger.warning('Invalid token')
        return None
    except InvalidId:
        flask.current_app.logger.warning('Bad identifier format in payload')
        return None
