import flask
import project.server.model as model


def get_blueprint(app, auth=None):
    url_prefix = app.config.get('BASE_URL_API') + '/<int:user_id>/groups'
    blueprint = flask.Blueprint('groups', __name__, url_prefix=url_prefix)
    blueprint.add_url_rule('/', view_func=auth.login_required(new_group), methods=['POST', 'PUT'], endpoint='new')
    blueprint.add_url_rule('/<int:group_id>', view_func=auth.login_required(single_group), methods=['GET'], endpoint='info')
    blueprint.add_url_rule('/<int:group_id>', view_func=auth.login_required(update_group), methods=['POST', 'PUT'], endpoint='update')
    blueprint.add_url_rule('/<int:group_id>', view_func=auth.login_required(delete_group), methods=['DEETE'], endpoint='delete')
    return blueprint


def new_group(user_id):
    user = model.search_user(user_id)
    if user is None:
        flask.abort(404, 'User not found')
    new_info = flask.request.json
    if not new_info or new_info is None:
        flask.abort(400, 'No information provided')
    name = new_info.get('name', None)
    if name is None:
        flask.abort(400, 'A group needs a name')
    group = user.create_group()
    group.info.update(new_info)
    # default value for private
    group.info['private'] = group.info.get('private', True)
    if(group.save()):
        return single_group(user_id, group.id)
    else:
        flask.abort(500, 'Error while saving new group')


def single_group(user_id, group_id):
    group = model.search_group(user_id, group_id)
    if group is None:
        flask.abort(404, 'Group not found')
    info = group.info
    checklists_info = list()
    for c in model.available_checklists(user_id, group_id):
        checklist_info = model.search_checklist(user_id, group_id, c).summary()
        checklist_info['uri'] = flask.url_for('checklists.info', user_id=user_id, group_id=group_id, checklist_id=c, _external=True)
        checklists_info.append(checklist_info)
    info['checklists'] = checklists_info
    info['uri'] = flask.url_for('groups.info', user_id=user_id, group_id=group_id, _external=True)
    info['id'] = group_id
    info['user'] = group.user.summary()
    info['user']['uri'] = flask.url_for('users.info', user_id=user_id, _external=True)
    return flask.jsonify(info)


def update_group(user_id, group_id):
    group = model.search_group(user_id, group_id)
    if group is None:
        flask.abort(404, 'User not found')
    new_info = flask.request.json
    if not new_info or new_info is None:
        flask.abort(400, 'No information')
    group.info.update(new_info)
    if(group.save()):
        return single_group(user_id, group.id)
    else:
        flask.abort(500, 'Error while saving group')


def delete_group(user_id, group_id):
    group = model.search_group(user_id, group_id)
    if group is None:
        flask.abort(404, 'Group not found')
    if group.delete():
        return flask.jsonify({'status': '200', 'message': 'Group {} deleted'.format(group_id)})
    else:
        flask.abort(500, 'Error while deleting group')
