import flask
from flask_httpauth import HTTPBasicAuth
from project.model import search_username


def create_auth():
    auth = HTTPBasicAuth()

    @auth.verify_password
    def verify_password(username, password):
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
