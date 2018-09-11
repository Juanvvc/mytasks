import flask
import project.views.users
import project.views.groups
import project.views.checklists
import project.server.auth
import logging


def get_blueprints(auth):
    return [
        project.views.users.get_blueprint(auth),
        project.views.groups.get_blueprint(auth),
        project.views.checklists.get_blueprint(auth)
    ]


def register(app=None, logger=None):
    if app is None:
        app = flask.current_app

    if logger is None:
        logger = logging

    auth = project.server.auth.create_auth()

    for blueprint in get_blueprints(auth):
        app.register_blueprint(blueprint)
