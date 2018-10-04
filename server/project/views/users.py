import flask
import project.model as model
import project.server.auth


def get_blueprint(auth=None):
    blueprint = flask.Blueprint('users', __name__)
    blueprint.add_url_rule('/users/', view_func=auth.login_required(users), methods=['GET'], endpoint='available')
    blueprint.add_url_rule('/users/<_id>', view_func=auth.login_required(single_user), methods=['GET'], endpoint='info')
    blueprint.add_url_rule('/login', view_func=auth.login_required(login), methods=['GET'], endpoint='login')

    return blueprint


def login():
    info = dict()
    info['token'] = project.server.auth.encode_auth_token(flask.g.user_id).decode()
    info['_id'] = str(flask.g.user_id)
    info['uri'] = flask.url_for('users.info', _id=str(flask.g.user_id), _external=True)
    info['status'] = 200
    return flask.jsonify(info)


def users():
    available_users = list()
    for user in model.available_users():
        info = user.copy()
        info['_id'] = str(info['_id'])
        info['uri'] = flask.url_for('users.info', _id=info['_id'], _external=True)
        available_users.append(info)
    return flask.jsonify(available_users)


def single_user(_id):
    user = model.search_element(model.User, _id)
    if user is None:
        flask.abort(404)
    info = user.summary()
    groups_info = list()
    only_public = (str(_id) != flask.g.user_id)

    for g in model.available_groups(_id, only_public=only_public):
        group_info = g.copy()
        group_info['_id'] = str(g['_id'])
        group_info['uri'] = flask.url_for('groups.info', _id=group_info['_id'], _external=True)
        groups_info.append(group_info)
    info['groups'] = groups_info
    info['uri'] = flask.url_for('users.info', _id=_id, _external=True)
    return flask.jsonify(info)
