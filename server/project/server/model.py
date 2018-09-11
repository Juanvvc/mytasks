#!/usr/bin/env python3

import os
import json
import shutil
import logging
from flask import current_app
import project.server.auth

logger = logging.getLogger(__name__)


METADATA_FILE = 'metadata.json'
PASSWORD_FIELDNAME = 'password_hash'


class User(object):
    def __init__(self, id):
        assert type(id) == int
        self.id = id
        if id not in available_users() or not os.path.isfile(self.filename()):
            raise Exception('User not found: {}'.format(id))
        with open(self.filename()) as json_data:
            try:
                self.info = json.load(json_data)
            except json.decoder.JSONDecodeError:
                logger.warning('Cannot decode %s. Using empty user.', self.filename())
                self.info = dict()

    def summary(self):
        """ Returns the summary of the userself.

        This method shouldn't return any dangerous information: passwords, hashes of passwords...
        Only data intented that can be publicly accessed is returned. """
        return dict(
            id=self.id,
            name=self.info.get('name', '')
        )

    def hash_password(self, password):
        """ Save a password hash in the user.

        Args:
            password (str): the password of the user. Only it hash is saved.
        """
        self.info[PASSWORD_FIELDNAME] = project.server.auth.hash_password(password).decode()

    def verify_password(self, password):
        """ Returns True if the password is verifiedself.

        If the user does not have a password hash, it is never verified. """
        if PASSWORD_FIELDNAME in self.info:
            try:
                return project.server.auth.check_password(self.info[PASSWORD_FIELDNAME], password)
            except ValueError as exc:
                logger.error(exc)
                return False
        else:
            return False

    def save(self):
        logger.debug('Saving user %s', self.id)
        with open(self.filename(), 'w') as json_file:
            json.dump(self.info, json_file, indent=4)
        return True

    def delete(self):
        logger.debug('Deleting user %s', self.id)
        shutil.rmtree(self.dirname())
        return True

    def filename(self):
        return os.path.join(self.dirname(), METADATA_FILE)

    def dirname(self):
        return os.path.join(current_app.config.get('DATA_DIR'), str(self.id))

    def create_group(self, info=None):
        existing_groups = available_groups(self.id)
        max_id = 0
        if existing_groups:
            max_id = max(existing_groups) + 1
        group_directory = os.path.join(self.dirname(), str(max_id))
        os.makedirs(group_directory, exist_ok=False)
        os.mknod(os.path.join(group_directory, METADATA_FILE))
        new_group = Group(self, max_id)
        if info is not None:
            new_group.info.update(info)
        return new_group


class Group(object):
    def __init__(self, user, id):
        assert type(user) == User
        assert type(id) == int
        self.user = user
        self.id = id

        existing_groups = available_groups(user.id)

        if self.id not in existing_groups:
            raise Exception('Group does not exist: {}/{}'.format(self.user.id, id))
        else:
            # load an existing group
            with open(self.filename()) as json_data:
                try:
                    self.info = json.load(json_data)
                except json.decoder.JSONDecodeError:
                    logger.warning('Cannot decode %s. Using empty group.', self.filename())
                    self.info = dict()

    def summary(self):
        return dict(
            id=self.id,
            name=self.info.get('name', ''),
            private=self.info.get('private', True)
        )

    def save(self):
        logger.debug('Saving group %s/%s', self.user.id, self.id)
        with open(self.filename(), 'w') as json_file:
            json.dump(self.info, json_file, indent=4)
        return True

    def delete(self):
        logger.debug('Deleting group %s/%s', self.user.id, self.id)
        # can only delete empty groups
        if available_checklists(self.user.id, self.id):
            return False
        shutil.rmtree(self.dirname())
        return True

    def filename(self):
        return os.path.join(self.dirname(), METADATA_FILE)

    def dirname(self):
        return os.path.join(self.user.dirname(), str(self.id))

    def create_checklist(self):
        existing_checklists = available_checklists(self.user.id, self.id)
        max_id = 0
        if existing_checklists:
            max_id = max(existing_checklists) + 1
        os.mknod(os.path.join(self.dirname(), '{}.json'.format(max_id)))
        return Checklist(self, max_id)


class Checklist(object):
    def __init__(self, group, id):
        assert type(group) == Group
        assert type(id) == int

        self.group = group
        self.id = id

        if not os.path.isfile(self.filename()):
            raise Exception('Checklist does not exist: {}/{}/{}'.format(self.group.user.id, self.group.id, id))
        else:
            # open a checklist
            with open(self.filename()) as json_data:
                try:
                    self.info = json.load(json_data)
                except json.decoder.JSONDecodeError:
                    logger.warning('Cannot decode file %s. Using empty information', self.filename())
                    self.info = dict()
                self.id = id

    def summary(self):
        return dict(
            id=self.id,
            name=self.info.get('name', '')
        )

    def save(self):
        logger.debug('Saving checklist %s/%s/%s', self.group.user.id, self.group.id, self.id)
        with open(self.filename(), 'w') as json_file:
            json.dump(self.info, json_file, indent=4)
        return True

    def delete(self):
        logger.debug('Deleting checklist %s/%s/%s', self.group.user.id, self.group.id, self.id)
        os.remove(self.filename())
        return True

    def filename(self):
        return os.path.join(self.group.dirname(), '{}.json'.format(self.id))


def available_users():
    users = list()
    if not os.path.isdir(current_app.config.get('DATA_DIR')):
        return []
    for directory in os.listdir(current_app.config.get('DATA_DIR')):
        try:
            user_directory = os.path.join(current_app.config.get('DATA_DIR'), directory)
            if os.path.isdir(user_directory) and os.path.isfile(os.path.join(user_directory, METADATA_FILE)):
                users.append(int(directory))
        except Exception as e:
            logger.warn(str(e))
    return users


def available_groups(user_id):
    user_directory = os.path.join(current_app.config.get('DATA_DIR'), str(user_id))
    if not os.path.isdir(user_directory):
        return []
    groups = list()
    for directory in os.listdir(user_directory):
        if directory == METADATA_FILE:
            continue
        try:
            if os.path.isfile(os.path.join(user_directory, directory, METADATA_FILE)):
                groups.append(int(directory))
        except Exception:
            logger.warning('Group with an invalid name: %s', directory)
    return groups


def available_checklists(user_id, group_id):
    group_directory = os.path.join(current_app.config.get('DATA_DIR'), str(user_id), str(group_id))
    if not os.path.isdir(group_directory):
        return []
    checklists = list()
    for filename in os.listdir(group_directory):
        if filename == METADATA_FILE:
            continue
        try:
            if filename.endswith('.json'):
                checklist_id = int(filename[:-5])
            else:
                checklist_id = int(filename)
            checklists.append(checklist_id)
        except Exception:
            logger.warning('Checklist with an invalid name: %s', filename)
    return checklists


def create_user(name, password=None):
    """ Creates a new user.

    Args:
        name (str): Name of the user
        password (str): Password of the user. If None, no password is created and the user cannot logon

    Returns:
        User: The new user
    """
    existing_users = available_users()
    max_id = 0
    if existing_users:
        max_id = max(available_users()) + 1
    user_directory = os.path.join(current_app.config.get('DATA_DIR'), str(max_id))
    # In case the directory exists but it is not yet a user, exist_ok=True
    os.makedirs(user_directory, exist_ok=True)
    os.mknod(os.path.join(user_directory, METADATA_FILE))
    user = User(max_id)
    user.info['name'] = name
    if password is not None:
        user.hash_password(password)
    if user.save():
        return user
    return None


def search_user(user_id):
    """ Gets a user, if exists.

    Args:
        user_id (int): The identifier of the user
    """
    if user_id in available_users():
        return User(user_id)
    return None


def search_username(username):
    """ Gets a user, if exists.

    Args:
        user_id (int): The identifier of the user
    """
    results = []
    for userid in available_users():
        user = User(userid)
        if user.info.get('name', None) == username:
            results.append(user)
    return results


def search_group(user_id, group_id):
    user = search_user(user_id)
    if user is None:
        return None
    if group_id in available_groups(user.id):
        return Group(user, group_id)
    return None


def search_checklist(user_id, group_id, checklist_id):
    group = search_group(user_id, group_id)
    if group is None:
        return None
    if checklist_id in available_checklists(user_id, group_id):
        return Checklist(group, checklist_id)
    return None
