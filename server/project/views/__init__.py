import project.views.users
import project.views.groups
import project.views.checklists
import project.server.auth
import flask


def get_blueprints(auth):
    return [
        project.views.users.get_blueprint(auth),
        project.views.groups.get_blueprint(auth),
        project.views.checklists.get_blueprint(auth)
    ]


def register(app):
    auth = project.server.auth.create_auth()

    for blueprint in get_blueprints(auth):
        app.register_blueprint(blueprint)

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(401)
    @app.errorhandler(500)
    def error_handler(error):
        return flask.make_response(flask.jsonify({'error_message': str(error), 'status': error.code}))
