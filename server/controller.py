#!/usr/bin/env python3

import flask
import model

app = flask.Flask(__name__)

BASE_URL_API = '/mytasks/api/v1.0'

# ------------------- GENERAL FUNCTIONS


@app.errorhandler(404)
@app.errorhandler(400)
@app.errorhandler(500)
def errorhandler(error):
    return flask.make_response(flask.jsonify({'error_message': str(error), 'status': error.code}))

# ------------------- USERS


@app.route(BASE_URL_API + '/', methods=['GET'])
def users():
    available_users = list()
    for user_id in model.available_users():
        info = model.search_user(user_id).summary()
        info['uri'] = flask.url_for('single_user', user_id=user_id, _external=True)
        available_users.append(info)
    return flask.jsonify(available_users)


@app.route(BASE_URL_API + '/<int:user_id>', methods=['GET'])
def single_user(user_id):
    user = model.search_user(user_id)
    if user is None:
        flask.abort(404)
    info = user.info
    groups_info = list()
    for g in model.available_groups(user_id):
        group_info = model.search_group(user_id, g).summary()
        group_info['uri'] = flask.url_for('single_group', user_id=user_id, group_id=g, _external=True)
        groups_info.append(group_info)
    info['groups'] = groups_info
    info['uri'] = flask.url_for('single_user', user_id=user_id, _external=True)
    info['id'] = user_id
    return flask.jsonify(info)

# ------------------- GROUPS


@app.route(BASE_URL_API + '/<int:user_id>/groups/<int:group_id>', methods=['GET'])
def single_group(user_id, group_id):
    group = model.search_group(user_id, group_id)
    if group is None:
        flask.abort(404, 'Group not found')
    info = group.info
    checklists_info = list()
    for c in model.available_checklists(user_id, group_id):
        checklist_info = model.search_checklist(user_id, group_id, c).summary()
        checklist_info['uri'] = flask.url_for('single_checklist', user_id=user_id, group_id=group_id, checklist_id=c, _external=True)
        checklists_info.append(checklist_info)
    info['checklists'] = checklists_info
    info['uri'] = flask.url_for('single_group', user_id=user_id, group_id=group_id, _external=True)
    info['id'] = group_id
    info['user'] = group.user.summary()
    info['user']['uri'] = flask.url_for('single_user', user_id=user_id, _external=True)
    return flask.jsonify(info)


@app.route(BASE_URL_API + '/<int:user_id>/groups/<int:group_id>', methods=['POST', 'PUT'])
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


@app.route(BASE_URL_API + '/<int:user_id>/groups', methods=['POST', 'PUT'])
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


@app.route(BASE_URL_API + '/<int:user_id>/groups/<int:group_id>', methods=['DELETE'])
def delete_group(user_id, group_id):
    group = model.search_group(user_id, group_id)
    if group is None:
        flask.abort(404, 'Group not found')
    if group.delete():
        return flask.jsonify({'status': '200', 'message': 'Group {} deleted'.format(group_id)})
    else:
        flask.abort(500, 'Error while deleting group')

# ------------------- CHECKLISTS


@app.route(BASE_URL_API + '/<int:user_id>/groups/<int:group_id>/checklists/<int:checklist_id>', methods=['GET'])
def single_checklist(user_id, group_id, checklist_id):
    checklist = model.search_checklist(user_id, group_id, checklist_id)
    if checklist is None:
        flask.abort(404, 'Checklist not found')
    info = checklist.info
    info['uri'] = flask.url_for('single_checklist', user_id=user_id, group_id=group_id, checklist_id=checklist_id, _external=True)
    info['id'] = checklist_id
    info['group'] = checklist.group.summary()
    info['group']['uri'] = flask.url_for('single_group', user_id=user_id, group_id=group_id, _external=True)
    info['user'] = checklist.group.user.summary()
    info['user']['uri'] = flask.url_for('single_user', user_id=user_id, _external=True)
    return flask.jsonify(info)


@app.route(BASE_URL_API + '/<int:user_id>/groups/<int:group_id>/checklists/<int:checklist_id>', methods=['POST', 'PUT'])
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


@app.route(BASE_URL_API + '/<int:user_id>/groups/<int:group_id>/checklists', methods=['POST', 'PUT'])
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


@app.route(BASE_URL_API + '/<int:user_id>/groups/<int:group_id>/checklists/<int:checklist_id>', methods=['DELETE'])
def delete_checklist(user_id, group_id, checklist_id):
    checklist = model.search_checklist(user_id, group_id, checklist_id)
    if checklist is None:
        flask.abort(404, 'Checklist not found')
    if checklist.delete():
        return flask.jsonify({'status': '200', 'message': 'Checklist {} deleted'.format(checklist_id)})
    else:
        flask.abort(500, 'Error while deleting checklist')
