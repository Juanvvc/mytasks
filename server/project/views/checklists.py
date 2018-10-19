import flask
import project.model as model
from bson.objectid import ObjectId
from bson.errors import InvalidId
import datetime


def get_blueprint(auth=None):
    blueprint = flask.Blueprint('checklists', __name__)
    blueprint.add_url_rule('/checklists/', view_func=auth.login_required(new_checklist), methods=['POST', 'PUT'], endpoint='new')
    blueprint.add_url_rule('/checklists/<_id>', view_func=auth.login_required(single_checklist), methods=['GET'], endpoint='info')
    blueprint.add_url_rule('/checklists/<_id>', view_func=auth.login_required(update_checklist), methods=['POST', 'PUT'], endpoint='update')
    blueprint.add_url_rule('/checklists/<_id>', view_func=auth.login_required(delete_checklist), methods=['DELETE'], endpoint='delete')
    blueprint.add_url_rule('/checklists/<_id>/clear', view_func=auth.login_required(clear_checklist), methods=['POST'], endpoint='clear')
    blueprint.add_url_rule('/checklists/<_id>/duplicate', view_func=auth.login_required(duplicate_checklist), methods=['POST'], endpoint='duplicate')
    blueprint.add_url_rule('/checklists/today', view_func=auth.login_required(today_checklist), methods=['GET'], endpoint='today')
    blueprint.add_url_rule('/checklists/history', view_func=auth.login_required(history_checklist), methods=['GET'], endpoint='history')

    return blueprint


def new_checklist():
    new_info = flask.request.json
    if not new_info or new_info is None:
        flask.abort(400, 'No information provided')

    # check the properties
    name = new_info.get('name', None)
    if name is None:
        flask.abort(400, 'A checklists needs a name')

    # ignore these properties
    new_info.pop('_id', None)

    # check the group
    group_id = new_info.get('parentid', None)
    if group_id is None:
        flask.abort(400, 'A checklists needs a group')
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
            if '_id' in item:
                # assume it is an external item
                real_item = model.search_element(model.Item, item['_id'])
                if real_item is None:
                    item_info = dict(name='NOT FOUND: {}'.format(str(item['_id'])), _id=str(item['_id']))
                else:
                    item_info = real_item.sane_info()
                    item_info['uri'] = flask.url_for('items.info', _id=str(real_item.id()), _external=True)
                new_items.append(item_info)
            else:
                # item has no _id: assume it is an internal document.
                new_items.append(item)
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
    try:
        if 'items' in new_info:
            new_items = []
            for item in new_info['items']:
                new_items.append(dict(_id=ObjectId(item['_id'])))
            new_info['items'] = new_items
    except InvalidId:
        flask.abort(400, 'Invalid identifiers in the items array')

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
    model.db.items.remove({'parentid': checklist.id()})

    if checklist.delete():
        return flask.jsonify({'status': 200, 'message': 'Checklist {} deleted'.format(_id)})
    else:
        flask.abort(500, 'Error while deleting checklist')

# --------------------------------------- Actions


def clear_checklist(_id):
    """ Remove all done items """
    checklist = model.search_element(model.Checklist, _id)
    # check the checklist exists and it is editable by the current user
    if checklist is None:
        flask.abort(404, 'Checklist not found')
    if not checklist.editable_by(flask.g.user_id):
        flask.abort(401, 'You are not allowed to edit this checklist')

    new_items = list()
    # remove all done items
    model.db.items.remove({'parentid': checklist.id(), 'checked': True})
    for item in checklist.info.get('items', []):
        # check if the items in the array still exist
        if model.db.items.find_one({'_id': item['_id']}):
            new_items.push(item)
    checklist.info['items'] = new_items
    checklist.save()
    return single_checklist(_id)


def duplicate_checklist(_id):
    """ Duplicates a checklist """
    checklist = model.search_element(model.Checklist, _id)
    # check the checklist exists and it is editable by the current user
    if checklist is None:
        flask.abort(404, 'Checklist not found')
    if not checklist.editable_by(flask.g.user_id):
        flask.abort(401, 'You are not allowed to edit this checklist')

    new_info = checklist.info.copy()

    # ignore these fields, if exist
    new_info.pop('_id', None)
    new_info.pop('items', None)

    # duplicate the checklist and its items
    new_checklist = checklist.parent().create_child(new_info)
    for item in checklist.info.get('items', []):
        if '_id' in item:
            # it is an external document: duplicate the item
            new_item = model.search_element(model.Item, item['_id'])
            import pprint
            pprint.pprint(new_item)
            if new_item is not None:
                new_checklist.create_child(new_item.info)
        else:
            # it is an internal item: create a new external item
            new_checklist.create_child(item)

    # save and return the new checklist
    if(new_checklist.save()):
        return single_checklist(checklist.id())
    else:
        flask.abort(500, 'Error while saving new checklist')


def today_checklist():
    """Gets a special checklist with unchecked items with a due_date before a week from today. """

    to_date = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=7), datetime.time(0, 0, 0)).isoformat()[:10]

    checklist = {
        'name': 'Today',
        'description': 'Due items before {}'.format(to_date),
        'hide_done_items': True,
        'items': []
    }

    groups = model.available_groups(flask.g.user_id)
    for g in groups:
        if '_id' not in g:
            continue
        checklists = model.available_checklists(g['_id'])
        for c in checklists:
            # checked not equal True also includes items without the checked field (default: checked=false)
            # also, do not include empty due_date
            filter = {'$and': [{'parentid': c['_id']}, {'checked': {'$not': {'$eq': True}}}, {'due_date': {'$gt': '', '$lt': to_date}}]}
            if model.db.items.count_documents(filter) > 0:
                items = model.db.items.find(filter)
                checklist['items'].append({'name': '# {} # {}'.format(g['name'], c['name'])})
                for i in items:
                    if '_id' in i:
                        i['_id'] = str(i['_id'])
                    if 'parentid' in i:
                        i['parentid'] = str(i['parentid'])
                    i['uri'] = flask.url_for('items.info', _id=i['_id'], _external=True)
                    checklist['items'].append(i)

    return flask.jsonify(checklist)


def history_checklist():
    """Gets a special checklist with checked items during the last week. """

    from_date = datetime.datetime.combine(datetime.date.today() - datetime.timedelta(days=7), datetime.time(0, 0, 0)).isoformat()[:10]

    checklist = {
        'name': 'Today',
        'description': 'Completed items after {}'.format(from_date),
        'hide_done_items': False,
        'items': []
    }

    groups = model.available_groups(flask.g.user_id)
    for g in groups:
        if '_id' not in g:
            continue
        checklists = model.available_checklists(g['_id'])
        for c in checklists:
            # checked not equal True also includes items without the checked field (default: checked=false)
            # also, do not include empty due_date
            filter = {'$and': [{'parentid': c['_id']}, {'checked': True}, {'done_date': {'$gte': from_date}}]}
            if model.db.items.count_documents(filter) > 0:
                items = model.db.items.find(filter)
                checklist['items'].append({'name': '# {}'.format(c['name'])})
                for i in items:
                    if '_id' in i:
                        i['_id'] = str(i['_id'])
                    if 'parentid' in i:
                        i['parentid'] = str(i['parentid'])
                    i['uri'] = flask.url_for('items.info', _id=i['_id'], _external=True)
                    checklist['items'].append(i)

    return flask.jsonify(checklist)
