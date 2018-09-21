import project.views.users
import project.views.groups
import project.views.checklists
import project.server.auth


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
