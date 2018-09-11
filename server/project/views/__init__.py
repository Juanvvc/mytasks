import project.views.users
import project.views.groups
import project.views.checklists


def get_blueprints(app, auth):
    return [
        project.views.users.get_blueprint(app, auth),
        project.views.groups.get_blueprint(app, auth),
        project.views.checklists.get_blueprint(app, auth)
    ]
