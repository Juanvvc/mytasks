import flask
from flask_httpauth import HTTPBasicAuth
from project.model import search_user
import logging


def create_auth(logger=None):
    if logger is None:
        logger = logging
    auth = HTTPBasicAuth()

    @auth.verify_password
    def verify_password(userid, password):
        logger.warning('Verifying password for user %s', userid)
        if not userid or not userid.isdigit():
            logger.warning('Username not valid: %s', userid)
            return False
        user = search_user(int(userid))
        if not user or not user.verify_password(password):
            logger.warning('Password not valid for userid: %s', userid)
            return False
        return True

    @auth.error_handler
    def auth_error():
        return flask.make_response(flask.jsonify(dict(error_message='Unauthorized', status=401)))

    return auth
