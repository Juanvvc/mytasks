import flask
import project.model as model


def get_blueprint(auth=None):
    url_prefix = '/<int:user_id>/groups/<int:group_id>/checklists'
    blueprint = flask.Blueprint('checklists', __name__, url_prefix=url_prefix)
    blueprint.add_url_rule('/', view_func=auth.login_required(new_checklist), methods=['POST', 'PUT'], endpoint='new')
    blueprint.add_url_rule('/<int:checklist_id>', view_func=auth.login_required(single_checklist), methods=['GET'], endpoint='info')
    blueprint.add_url_rule('/<int:checklist_id>', view_func=auth.login_required(update_checklist), methods=['POST', 'PUT'], endpoint='update')
    blueprint.add_url_rule('/<int:checklist_id>', view_func=auth.login_required(delete_checklist), methods=['DELETE'], endpoint='delete')
    return blueprint


def new_checklist(user_id, group_id):
    group = model.search_group(user_id, group_id)
    if group is None:
        flask.abort(404, 'Group not found')
    new_info = flask.request.json
    if not new_info or new_info is None:
        flask.abort(400, 'No information provided')
    name = new_info.get('name', None)
    if name is None:
        flask.abort(400, 'A checklists needs a name')
    checklist = group.create_checklist()
    checklist.info.update(new_info)
    if(checklist.save()):
        return single_checklist(user_id, group_id, checklist.id)
    else:
        flask.abort(500, 'Error while saving new checklist')


def single_checklist(user_id, group_id, checklist_id):
    checklist = model.search_checklist(user_id, group_id, checklist_id)
    if checklist is None:
        flask.abort(404, 'Checklist not found')
    info = checklist.info
    info['uri'] = flask.url_for('checklists.info', user_id=user_id, group_id=group_id, checklist_id=checklist_id, _external=True)
    info['id'] = checklist_id
    info['group'] = checklist.group.summary()
    info['group']['uri'] = flask.url_for('groups.info', user_id=user_id, group_id=group_id, _external=True)
    info['user'] = checklist.group.user.summary()
    info['user']['uri'] = flask.url_for('users.info', user_id=user_id, _external=True)
    return flask.jsonify(info)


def update_checklist(user_id, group_id, checklist_id):
    checklist = model.search_checklist(user_id, group_id, checklist_id)
    if checklist is None:
        flask.abort(404, 'Checklist not found')
    new_info = flask.request.json
    if not new_info or new_info is None:
        flask.abort(400, 'No information provided')
    checklist.info.update(new_info)
    if(checklist.save()):
        return single_checklist(user_id, group_id, checklist_id)
    else:
        flask.abort(500, 'Error while saving checklist')


def delete_checklist(user_id, group_id, checklist_id):
    checklist = model.search_checklist(user_id, group_id, checklist_id)
    if checklist is None:
        flask.abort(404, 'Checklist not found')
    if checklist.delete():
        return flask.jsonify({'status': 200, 'message': 'Checklist {} deleted'.format(checklist_id)})
    else:
        flask.abort(500, 'Error while deleting checklist')
