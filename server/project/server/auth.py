
import logging
from flask_httpauth import HTTPBasicAuth

__auth = None


def get_auth(app, logger=None):
    global __auth

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

    __auth = auth

    return __auth
