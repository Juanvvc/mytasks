import flask
import project.model as model


def get_blueprint(auth=None):
    blueprint = flask.Blueprint('users', __name__)
    blueprint.add_url_rule('/', view_func=auth.login_required(users), methods=['GET'], endpoint='available')
    blueprint.add_url_rule('/<user_id>', view_func=auth.login_required(single_user), methods=['GET'], endpoint='info')
    blueprint.add_url_rule('/login', view_func=auth.login_required(users), methods=['GET'], endpoint='login')

    return blueprint


def login():
    return single_user(flask.g.user_id)


def users():
    available_users = list()
    for user in model.available_users():
        info = user.copy()
        info['_id'] = str(info['_id'])
        info['uri'] = flask.url_for('users.info', user_id=info['_id'], _external=True)
        available_users.append(info)
    return flask.jsonify(available_users)


def single_user(user_id):
    user = model.search_user(user_id)
    if user is None:
        flask.abort(404)
    info = user.summary()
    groups_info = list()
    for g in model.available_groups(user_id):
        group_info = g.copy()
        group_info['_id'] = str(g['_id'])
        group_info['userid'] = str(g['_id'])
        group_info['uri'] = flask.url_for('groups.info', user_id=user_id, group_id=group_info['_id'], _external=True)
        groups_info.append(group_info)
    info['groups'] = groups_info
    info['uri'] = flask.url_for('users.info', user_id=user_id, _external=True)
    return flask.jsonify(info)
