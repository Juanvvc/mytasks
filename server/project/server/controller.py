#!/usr/bin/env python3


import project.server.model as model
import flask

from project.server import app, auth, logger

# ------------------- GENERAL FUNCTIONS


@app.errorhandler(404)
@app.errorhandler(400)
@app.errorhandler(500)
def errorhandler(error):
    return flask.make_response(flask.jsonify({'error_message': str(error), 'status': error.code}))


@auth.verify_password
def verify_password(userid, password):
    logger.warning('Verifying password for user %s', userid)
    if not userid or not userid.isdigit():
        logger.warning('Username not valid: %s', userid)
        return False
    user = model.search_user(int(userid))
    if not user or not user.verify_password(password):
        logger.warning('Password not valid for userid: %s', userid)
        return False
    return True

# ------------------- USERS


@app.route(app.config.get('BASE_URL_API') + '/', methods=['GET'])
@auth.login_required
def users():
    available_users = list()
    for user_id in model.available_users():
        info = model.search_user(user_id).summary()
        info['uri'] = flask.url_for('single_user', user_id=user_id, _external=True)
        available_users.append(info)
    return flask.jsonify(available_users)


@app.route(app.config.get('BASE_URL_API') + '/<int:user_id>', methods=['GET'])
@auth.login_required
def single_user(user_id):
    user = model.search_user(user_id)
    if user is None:
        flask.abort(404)
    info = user.summary()
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


@app.route(app.config.get('BASE_URL_API') + '/<int:user_id>/groups/<int:group_id>', methods=['GET'])
@auth.login_required
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


@app.route(app.config.get('BASE_URL_API') + '/<int:user_id>/groups/<int:group_id>', methods=['POST', 'PUT'])
@auth.login_required
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


@app.route(app.config.get('BASE_URL_API') + '/<int:user_id>/groups', methods=['POST', 'PUT'])
@auth.login_required
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


@app.route(app.config.get('BASE_URL_API') + '/<int:user_id>/groups/<int:group_id>', methods=['DELETE'])
@auth.login_required
def delete_group(user_id, group_id):
    group = model.search_group(user_id, group_id)
    if group is None:
        flask.abort(404, 'Group not found')
    if group.delete():
        return flask.jsonify({'status': '200', 'message': 'Group {} deleted'.format(group_id)})
    else:
        flask.abort(500, 'Error while deleting group')

# ------------------- CHECKLISTS


@app.route(app.config.get('BASE_URL_API') + '/<int:user_id>/groups/<int:group_id>/checklists/<int:checklist_id>', methods=['GET'])
@auth.login_required
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


@app.route(app.config.get('BASE_URL_API') + '/<int:user_id>/groups/<int:group_id>/checklists/<int:checklist_id>', methods=['POST', 'PUT'])
@auth.login_required
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


@app.route(app.config.get('BASE_URL_API') + '/<int:user_id>/groups/<int:group_id>/checklists', methods=['POST', 'PUT'])
@auth.login_required
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


@app.route(app.config.get('BASE_URL_API') + '/<int:user_id>/groups/<int:group_id>/checklists/<int:checklist_id>', methods=['DELETE'])
@auth.login_required
def delete_checklist(user_id, group_id, checklist_id):
    checklist = model.search_checklist(user_id, group_id, checklist_id)
    if checklist is None:
        flask.abort(404, 'Checklist not found')
    if checklist.delete():
        return flask.jsonify({'status': '200', 'message': 'Checklist {} deleted'.format(checklist_id)})
    else:
        flask.abort(500, 'Error while deleting checklist')
