import flask
import project.model as model


def get_blueprint(auth=None):
    blueprint = flask.Blueprint('checklists', __name__)
    blueprint.add_url_rule('/checklists/', view_func=auth.login_required(new_checklist), methods=['POST', 'PUT'], endpoint='new')
    blueprint.add_url_rule('/checklists/<_id>', view_func=auth.login_required(single_checklist), methods=['GET'], endpoint='info')
    blueprint.add_url_rule('/checklists/<_id>', view_func=auth.login_required(update_checklist), methods=['POST', 'PUT'], endpoint='update')
    blueprint.add_url_rule('/checklists/<_id>', view_func=auth.login_required(delete_checklist), methods=['DELETE'], endpoint='delete')
    return blueprint


def new_checklist():
    new_info = flask.request.json
    if not new_info or new_info is None:
        flask.abort(400, 'No information provided')

    # check the properties
    name = new_info.get('name', None)
    if name is None:
        flask.abort(400, 'A checklists needs a name')

    # check the group
    group_id = new_info.get('_parentid', None)
    if group_id is None:
        flask.abort(400, 'A checklists needs a name')
    group = model.search_element(model.Group, group_id)
    if group is None:
        flask.abort(404, 'Group not found')

    # create the checklist
    checklist = group.create_child(new_info)
    if(checklist.save()):
        return single_checklist(checklist.id())
    else:
        flask.abort(500, 'Error while saving new checklist')


def single_checklist(_id):
    checklist = model.search_element(model.Checklist, _id)
    # checl the list exists
    if checklist is None:
        flask.abort(404, 'Checklist not found')
    # check the user is allowed to access the list
    if not checklist.visible_by(flask.g.user_id):
        flask.abort(401, 'Not allowed to access this checklist')

    info = checklist.sane_info()
    info['uri'] = flask.url_for('checklists.info', _id=_id, _external=True)

    # convert the items list to an Item list
    new_items = []
    if 'items' in info:
        for item in info['items']:
            real_item = model.search_element(model.Item, item['_id'])
            item_info = real_item.sane_info()
            item_info['uri'] = flask.url_for('items.info', _id=str(real_item.id()))
            new_items.append(item_info)
        info['items'] = new_items

    return flask.jsonify(info)


def update_checklist(_id):
    checklist = model.search_element(model.Checklist, _id)
    # check the checklist exists and it is editable by the current user
    if checklist is None:
        flask.abort(404, 'Checklist not found')
    if not checklist.editable_by(flask.g.user_id):
        flask.abort(401, 'Your are not allowed to edit this checklist')

    new_info = flask.request.json
    if not new_info or new_info is None:
        flask.abort(400, 'No information')

    # is an array of items is passed, update only the Item IDs
    if 'items' in new_info:
        new_items = []
        for item in new_info['items']:
            new_items.append(dict(_id=item['_id']))
        new_info['items'] = new_items
    checklist.info.update(new_info)

    if(checklist.save()):
        return single_checklist(_id)
    else:
        flask.abort(500, 'Error while saving checklist')


def delete_checklist(_id):
    checklist = model.search_element(model.Checklist, _id)
    # check the checklist exists and it is editable by the current user
    if checklist is None:
        flask.abort(404, 'Checklist not found')
    if not checklist.editable_by(flask.g.user_id):
        flask.abort(401, 'You are not allowed to edit this checklist')

    # delete all items in the list
    model.db.items.remove({'_parentid': checklist.id()})

    if checklist.delete():
        return flask.jsonify({'status': 200, 'message': 'Checklist {} deleted'.format(_id)})
    else:
        flask.abort(500, 'Error while deleting checklist')
