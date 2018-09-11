import project.views.users
import project.views.groups
import project.views.checklists
import project.server.auth


def get_blueprints(app, auth):
    return [
        project.views.users.get_blueprint(app, auth),
        project.views.groups.get_blueprint(app, auth),
        project.views.checklists.get_blueprint(app, auth)
    ]


def register(app=None):
    if app is None:
        import flask
        app = flask.current_app
    auth = project.server.auth.get_auth()
    for blueprint in get_blueprints(app, auth):
        app.register_blueprint(blueprint)
