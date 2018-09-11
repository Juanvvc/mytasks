import flask
import project.server.model as model


def get_blueprint(app, auth=None):
    url_prefix = app.config.get('BASE_URL_API')
    blueprint = flask.Blueprint('users', __name__, url_prefix=url_prefix)
    blueprint.add_url_rule('/', view_func=auth.login_required(users), methods=['GET'], endpoint='available')
    blueprint.add_url_rule('/<int:user_id>', view_func=auth.login_required(single_user), methods=['GET'], endpoint='info')
    return blueprint


def users():
    available_users = list()
    for user_id in model.available_users():
        info = model.search_user(user_id).summary()
        info['uri'] = flask.url_for('users.info', user_id=user_id, _external=True)
        available_users.append(info)
    return flask.jsonify(available_users)


def single_user(user_id):
    user = model.search_user(user_id)
    if user is None:
        flask.abort(404)
    info = user.summary()
    groups_info = list()
    for g in model.available_groups(user_id):
        group_info = model.search_group(user_id, g).summary()
        group_info['uri'] = flask.url_for('groups.info', user_id=user_id, group_id=g, _external=True)
        groups_info.append(group_info)
    info['groups'] = groups_info
    info['uri'] = flask.url_for('users.info', user_id=user_id, _external=True)
    info['id'] = user_id
    return flask.jsonify(info)
