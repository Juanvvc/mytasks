
import logging
import flask
from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import Bcrypt
from flask import current_app

__auth = None
__app = None


def get_auth(logger=None):
    global __auth, __bcrypt

    if logger is None:
        logger = logging

    if __auth is not None:
        return __auth

    import project.server.model as model

    auth = HTTPBasicAuth()

    @auth.verify_password
    def verify_password(userid, password):
        logger.warning('Verifying password for user %s', userid)
        if not userid or not userid.isdigit():
            logger.warning('Username not valid: %s', userid)
            return False
        user = model.search_user(int(userid))
        if not user or not user.verify_password(password):
            logger.warning('Password not valid for userid: %s', userid)
            return False
        return True

    @auth.error_handler
    def auth_error():
        return flask.make_response(flask.jsonify(dict(error_message='Unauthorized', status=401)))

    __auth = auth

    return __auth


def hash_password(password):
    bcrypt = Bcrypt(flask.current_app)
    return bcrypt.generate_password_hash(password, current_app.config.get('BCRYPT_LOG_ROUNDS'))


def check_password(hashed_password, password):
    bcrypt = Bcrypt(flask.current_app)
    return bcrypt.check_password_hash(hashed_password, password)
