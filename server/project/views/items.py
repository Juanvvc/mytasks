import flask
import project.model as model


def get_blueprint(auth=None):
    blueprint = flask.Blueprint('items', __name__)
    blueprint.add_url_rule('/items/', view_func=auth.login_required(new_item), methods=['POST', 'PUT'], endpoint='new')
    blueprint.add_url_rule('/items/<_id>', view_func=auth.login_required(single_item), methods=['GET'], endpoint='info')
    blueprint.add_url_rule('/items/<_id>', view_func=auth.login_required(update_item), methods=['POST', 'PUT'], endpoint='update')
    blueprint.add_url_rule('/items/<_id>', view_func=auth.login_required(delete_item), methods=['DELETE'], endpoint='delete')
    return blueprint


def new_item():
    new_info = flask.request.json
    if not new_info or new_info is None:
        flask.abort(400, 'No information provided')

    # check the properties
    name = new_info.get('name', None)
    if name is None:
        flask.abort(400, 'An item needs a name')

    # check the checklist
    checklist_id = new_info.get('parentid', None)
    if checklist_id is None:
        flask.abort(400, 'A checklists needs a name')
    checklist = model.search_element(model.Checklist, checklist_id)
    if checklist is None:
        flask.abort(404, 'Group not found')

    # create the checklist
    item = checklist.create_child(new_info)
    if(checklist.save()):
        return single_item(item.id())
    else:
        flask.abort(500, 'Error while saving new item')


def single_item(_id):
    item = model.search_element(model.Item, _id)
    # check the list exists
    if item is None:
        flask.abort(404, 'Item not found')
    # check the user is allowed to access the list
    if not item.visible_by(flask.g.user_id):
        flask.abort(401, 'Not allowed to access this item')

    info = item.sane_info()
    info['uri'] = flask.url_for('items.info', _id=_id, _external=True)
    return flask.jsonify(info)


def update_item(_id):
    item = model.search_element(model.Item, _id)
    # check the checklist exists and it is editable by the current user
    if item is None:
        flask.abort(404, 'Item not found')
    if not item.editable_by(flask.g.user_id):
        flask.abort(401, 'Your are not allowed to edit this item')

    new_info = flask.request.json
    if not new_info or new_info is None:
        flask.abort(400, 'No information')
    item.info.update(new_info)
    if(item.save()):
        return single_item(_id)
    else:
        flask.abort(500, 'Error while saving item')


def delete_item(_id):
    item = model.search_element(model.Item, _id)
    # check the checklist exists and it is editable by the current user
    if item is None:
        flask.abort(404, 'Item not found')
    if not item.editable_by(flask.g.user_id):
        flask.abort(401, 'You are not allowed to edit this item')

    # delete the item from the checklist
    if 'parentid' in item.info:
        checklist = model.search_element(model.Checklist, item.info['parentid'])
        if checklist is None:
            flask.current_app.logger.error('Removing Item %s and checklist not found', _id)
        elif not checklist.delete_child(_id):
            flask.current_app.logger.error('Cannot remove Item %s from checklist %s', _id, checklist.id())
    else:
        flask.current_app.logger.error('Item %s doesn\'t belong to a checklist', _id)

    if item.delete():
        return flask.jsonify({'status': 200, 'message': 'Item {} deleted'.format(_id)})
    else:
        flask.abort(500, 'Error while deleting checklist')
