import flask
import project.model as model


def get_blueprint(auth=None):
    blueprint = flask.Blueprint('groups', __name__)
    blueprint.add_url_rule('/groups/', view_func=auth.login_required(new_group), methods=['POST', 'PUT'], endpoint='new')
    blueprint.add_url_rule('/groups/<_id>', view_func=auth.login_required(single_group), methods=['GET'], endpoint='info')
    blueprint.add_url_rule('/groups/<_id>', view_func=auth.login_required(update_group), methods=['POST', 'PUT'], endpoint='update')
    blueprint.add_url_rule('/groups/<_id>', view_func=auth.login_required(delete_group), methods=['DELETE'], endpoint='delete')
    return blueprint


def new_group():
    # get the current user. The group is goung to be created for him
    user_id = flask.g.user_id
    user = model.search_element(model.User, user_id)
    if user is None:
        flask.abort(404, 'User not found')

    new_info = flask.request.json
    # check properties
    if not new_info or new_info is None:
        flask.abort(400, 'No information provided')
    name = new_info.get('name', None)
    if name is None:
        flask.abort(400, 'A group needs a name')

    group = user.create_child(new_info)
    # default value for private
    group.info['private'] = group.info.get('private', True)
    if(group.save()):
        return single_group(group.id())
    else:
        flask.abort(500, 'Error while saving new group')


def single_group(_id):
    group = model.search_element(model.Group, _id)
    # check the group exists
    if group is None:
        flask.abort(404, 'Group not found')
    # check the user is allowed to see the group
    if not group.visible_by(flask.g.user_id):
        flask.abort(401, 'Not allowed to access group')

    info = group.sane_info()
    checklists_info = list()
    for c in model.available_checklists(_id):
        checklist_info = dict()
        checklist_info['_id'] = str(c['_id'])
        checklist_info['name'] = str(c['name'])
        checklist_info['uri'] = flask.url_for('checklists.info', _id=checklist_info['_id'], _external=True)
        checklists_info.append(checklist_info)
    info['checklists'] = checklists_info
    info['uri'] = flask.url_for('groups.info', _id=_id, _external=True)
    return flask.jsonify(info)


def update_group(_id):
    group = model.search_element(model.Group, _id)
    # check the group exist
    if group is None:
        flask.abort(404, 'User not found')
    # check the group is editable by this user
    if not group.editable_by(flask.g.user_id):
        flask.abort(401, 'Not allows to change this group')

    new_info = flask.request.json
    if not new_info or new_info is None:
        flask.abort(400, 'No information')
    group.info.update(new_info)
    if(group.save()):
        return single_group(_id)
    else:
        flask.abort(500, 'Error while saving group')


def delete_group(_id):
    group = model.search_element(model.Group, _id)
    # check the group exist
    if group is None:
        flask.abort(404, 'Group not found')
    # check the group is editable by this user
    if not group.editable_by(flask.g.user_id):
        flask.abort(401, 'Not allowed to delete this group')

    # check the group is empty
    if model.db.checklists.count({'parentid': group.id()}) > 0:
        flask.abort(401, 'Group is not empty')

    if group.delete():
        return flask.jsonify({'status': 200, 'message': 'Group {} deleted'.format(_id)})
    else:
        flask.abort(500, 'Error while deleting group')
