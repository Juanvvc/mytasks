#!/usr/bin/env python3

import logging
import bcrypt
import pymongo
from bson.objectid import ObjectId
from bson.errors import InvalidId


logger = logging.getLogger(__name__)
PASSWORD_FIELDNAME = 'password_hash'

# The Flask app must change this to the real path
client = None
db = None


def configure_model(app):
    """ Configures the model from a Flask app.

    Attrs:
        :app (Flask): The Flask application to read the configuration from
    """
    global logger, client, db
    client = pymongo.MongoClient(app.config.get('MONGOURL'))
    db = client[app.config.get('MONGODB', 'mytasks')]
    logger = app.logger


class User(object):
    def __init__(self, id):
        if id is None:
            # create a new user
            id = db.users.insert_one({}).inserted_id

        self.info = db.users.find_one({'_id': id})
        if self.info is None:
            raise Exception('User not found: {}'.format(id))

    def id(self):
        """ A convenience method to get the bson.objectid.ObjectId of this user """
        if '_id' not in self.info:
            raise Exception('Somehow, the user has no identifier')
        return self.info['_id']

    def summary(self):
        """ Returns the summary of the userself.

        This method shouldn't return any dangerous information: passwords, hashes of passwords...
        Only data intented that can be publicly accessed is returned. """
        return dict(
            _id=str(self.id()),
            name=self.info.get('name', '')
        )

    def hash_password(self, password):
        """ Save a password hash in the user.

        Args:
            password (str): the password of the user. Only it hash is saved.
        """
        self.info[PASSWORD_FIELDNAME] = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password):
        """ Returns True if the password is verifiedself.

        If the user does not have a password hash, it is never verified. """
        if PASSWORD_FIELDNAME in self.info:
            try:
                return bcrypt.checkpw(password.encode(), self.info[PASSWORD_FIELDNAME].encode())
            except ValueError as exc:
                logger.error(exc)
                return False
        else:
            return False

    def save(self):
        logger.debug('Saving user %s', self.id())
        db.users.save(self.info)
        return True

    def delete(self):
        logger.debug('Deleting user %s', self.id())
        # First, remove all groups and checklists owned by this user
        db.groups.remove({'userid': self.id()})
        db.checklists.remove({'userid': self.id()})
        # Then, remove the user
        db.users.remove({'_id': self.id()})
        return True

    def create_group(self, info):
        """ Creates a new group owned by this user.

        If info includes a userid, it is ignored
        """
        new_group = Group(self, None)
        new_info = info.copy()
        # the deafult value for privacy
        new_info['private'] = new_info.get('private', True)
        # userid is ignored, it exist
        new_info.pop('userid', None)
        # update the info and save
        new_group.info.update(new_info)
        new_group.save()
        return new_group


class Group(object):
    """ Groups are private unless explicitely configured as non private """
    def __init__(self, user, id):
        assert type(user) == User
        if id is None:
            # create a new group
            id = db.groups.insert_one({'userid': user.id()}).inserted_id

        self.info = db.groups.find_one({'_id': id})
        if self.info is None:
            raise Exception('Group not found: {}'.format(id))
        self.user = user

    def id(self):
        """ A convenience method to get the bson.objectid.ObjectId of this group """
        if '_id' not in self.info:
            raise Exception('Somehow, the group has no identifier')
        return self.info['_id']

    def summary(self):
        """ Returns the summary of the group.

        This method shouldn't return any dangerous information.
        Only serializable intented that can be publicly accessed is returned. """
        return dict(
            _id=str(self.id()),
            name=self.info.get('name', ''),
            userid=str(self.info.get('userid', '')),
            private=self.info.get('private', True)
        )

    def save(self):
        logger.debug('Saving group %s/%s', self.user.id(), self.id())
        db.groups.save(self.info)
        return True

    def delete(self):
        """ You can only remove empty groups """
        logger.debug('Deleting group %s/%s', self.user.id(), self.id())
        # You cannot remove the group if there are documents in it
        if db.checklists.count_documents({'groupid': self.id()}) > 0:
            return False
        # Then, remove the user
        db.groups.remove({'_id': self.id()})
        return True

    def create_checklist(self, info):
        """ Creates a new checklist in this group and owned by its user.

        If info includes a groupid, it is ignored.
        """

        new_checklist = Checklist(self, None)
        new_info = info.copy()
        # groupid, if exists, is ignored
        new_info.pop('groupid', None)
        # update the info and save
        new_checklist.info.update(new_info)
        new_checklist.save()
        return new_checklist

    def visible_by(self, user_id):
        """ Returns True if user_id is allowed to access the group """
        assert self.user is not None
        # a user can access its own groups always
        if str(user_id) == str(self.user.id()):
            return True
        # a different user can access only to non private groups
        return not self.info.get('private', True)

    def editable_by(self, user_id):
        """ Returns True if the user_id is allowed to edit or remove this group """
        # only owners can edit or remove groups
        assert self.user is not None
        return str(self.user.id()) == str(user_id)


class Checklist(object):
    def __init__(self, group, id):
        assert type(group) == Group
        if id is None:
            # create a new checklist
            id = db.checklists.insert_one({'groupid': group.id()}).inserted_id

        self.info = db.checklists.find_one({'_id': id})
        if self.info is None:
            raise Exception('Checklist not found: {}'.format(id))
        self.group = group

    def id(self):
        """ A convenience method to get the bson.objectid.ObjectId of this checklist """
        if '_id' not in self.info:
            raise Exception('Somehow, the group has no identifier')
        return self.info['_id']

    def summary(self):
        """ Returns the summary of the checklist.

        This method shouldn't return any dangerous information.
        Only data intented that can be publicly accessed is returned. """
        return dict(
            _id=str(self.id()),
            name=self.info.get('name', ''),
            groupid=str(self.info.get('groupid', '')),
        )

    def save(self):
        logger.debug('Saving checklist %s/%s/%s', self.group.user.id(), self.group.id(), self.id())
        db.checklists.save(self.info)
        return True

    def delete(self):
        logger.debug('Deleting checklist %s/%s/%s', self.group.user.id(), self.group.id(), self.id())
        db.checklists.remove({'_id': self.id()})
        return True

    def visible_by(self, user_id):
        """ Returns True if user_id is allowed to access the checklist """
        assert self.group is not None
        return self.group.visible_by(user_id)

    def editable_by(self, user_id):
        """ Returns True if the user_id is allowed to edit or remove this group """
        assert self.group is not None
        return self.group.editable_by(user_id)


def available_users():
    """  Returns: A pymongo.cursor.Cursor with the available users """
    return db.users.find({}, {'name': 1})


def available_groups(user_id, only_public=False):
    """
    Attrs:
        user_id: str or ObjectId of the user
        only_public: if True, returns only public groups. Default: False

    Returns:
        A pymongo.cursor.Cursor with the available groups in a user """
    if type(user_id) == str:
        try:
            user_id = ObjectId(user_id)
        except InvalidId:
            return []
    if only_public:
        return db.groups.find({'userid': user_id, 'private': False}, {'name': 1, 'private': 1})
    return db.groups.find({'userid': user_id}, {'name': 1, 'private': 1})


def available_checklists(group_id):
    """  Returns: A pymongo.cursor.Cursor with the available checklists in a group """
    if type(group_id) == str:
        try:
            group_id = ObjectId(group_id)
        except InvalidId:
            return []
    return db.checklists.find({'groupid': group_id}, {'name': 1, 'userid': 1, 'groupid': 1})


def create_user(name, password=None):
    """ Creates a new user.

    Args:
        name (str): Name of the user
        password (str): Password of the user. If None, no password is created and the user cannot logon

    Returns:
        User: The new user
    """
    user = User(None)
    user.info['name'] = name
    if password is not None:
        user.hash_password(password)
    if user.save():
        return user
    return user


def search_user(userid):
    if type(userid) == str:
        try:
            userid = ObjectId(userid)
        except InvalidId:
            logger.warn('Invalid user_id: %s', userid)
            return None
    try:
        return User(userid)
    except Exception:
        logger.warn('Something happened constructing the user: %s', userid)
        return None


def search_username(name):
    """ Gets a user, if exists.

    Args:
        user_id (int): The identifier of the user
    """
    userinfo = db.users.find_one({'name': name})
    if userinfo is None:
        logger.warn('User not found: %s', name)
        return None
    return User(userinfo['_id'])


def search_group(groupid):
    if type(groupid) == str:
        try:
            groupid = ObjectId(groupid)
        except InvalidId:
            logger.warn('Invalid group_id: %s', groupid)
            return None
    groupinfo = db.groups.find_one({'_id': groupid})
    if groupinfo is None:
        logger.warn('Checklist not found: %s', groupid)
        return None
    user = search_user(groupinfo['userid'])
    if user is None:
        logger.warn('Group found, but user doesn\'t: %s', groupid)
        return None
    try:
        return Group(user, groupid)
    except Exception:
        logger.warn('Something happened constructing the group: %s', groupid)
        return None


def search_checklist(checklistid):
    if type(checklistid) == str:
        try:
            checklistid = ObjectId(checklistid)
        except InvalidId:
            logger.warn('Invalid checklist_id: %s', checklistid)
            return None
    checklistinfo = db.checklists.find_one({'_id': checklistid})
    if checklistinfo is None:
        logger.warn('Checklist not found: %s', checklistid)
        return None
    group = search_group(checklistinfo['groupid'])
    if group is None:
        logger.warn('Checklist found, but group doesn\'t: %s', checklistid)
        return None
    try:
        return Checklist(group, checklistid)
    except Exception:
        logger.warn('Something happened constructing the checklist: %s', checklistid)
        return None
