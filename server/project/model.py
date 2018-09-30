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


class BaseElement(object):
    def __init__(self, collection, parent=None, children_class=None):
        """
        You must include an _id in the self.info dictionary in your constructor.

        Args:
            collection: a db.COLLECTION for this element
            parent: The BaseElement which contains this one, if any
        """
        self.info = dict(_id=None)
        self.collection = collection
        self.parent = parent
        self.children_class = children_class

    def id(self):
        """ A convenience method to get the bson.objectid.ObjectId of this element """
        if '_id' not in self.info:
            raise Exception('Somehow, the element has no identifier')
        return self.info['_id']

    def summary(self):
        """ Returns the summary of the element.

        This method shouldn't return any dangerous information: passwords, hashes of passwords...
        Only data intented that can be publicly accessed is returned. """

        summary = dict(
            _id=str(self.id()),
            name=self.info.get('name', '')
        )

        if self.parent is not None:
            summary.update({'_parentid': self.parent.id()})

        return summary

    def save(self):
        self.collection.save(self.info)
        return True

    def visible_by(self, user_id):
        """ Returns True if user_id is allowed to access the BaseElement """
        assert self.parent is not None
        return self.parent.visible_by(user_id)

    def editable_by(self, user_id):
        """ Returns True if the user_id is allowed to edit or remove this BaseElement """
        assert self.parent is not None
        return self.parent.editable_by(user_id)

    def delete(self):
        self.collection.remove({'_id': self.id()})
        return True

    def create_child(self, info):
        """ Creates a new chil in this element

        If info includes a _parentid, it is ignored
        """
        if self.children_class is None:
            raise Exception('This element type cannot have children')
        new_child = self.children_class(self, None)
        # update the info and save
        new_child.info.update(info)
        new_child.info.update({'_parentid': self.id()})
        new_child.save()
        return new_child


class User(BaseElement):
    def __init__(self, id):
        super().__init__(db.users)
        if id is None:
            # create a new user
            id = db.users.insert_one({}).inserted_id

        new_info = db.users.find_one({'_id': id})
        if new_info is None:
            raise Exception('User not found: {}'.format(id))
        self.info.update(new_info)
        self.children_class = Group

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


class Group(BaseElement):
    """ Groups are private unless explicitely configured as non private """
    def __init__(self, user, id):
        super().__init__(db.groups, parent=user)
        assert type(user) == User
        if id is None:
            # create a new group
            id = db.groups.insert_one({'_parentid': user.id(), 'private': True}).inserted_id

        new_info = db.groups.find_one({'_id': id})
        if new_info is None:
            raise Exception('Group not found: {}'.format(id))
        self.info.update(new_info)
        self.children_class = Checklist

    def summary(self):
        return super().summary().update({'private': self.info.get('private', True)})

    def visible_by(self, user_id):
        """ Returns True if user_id is allowed to access the group """
        assert self.parent is not None
        # a user can access its own groups always
        if str(user_id) == str(self.parent.id()):
            return True
        # a different user can access only to non private groups
        return not self.info.get('private', True)

    def editable_by(self, user_id):
        """ Returns True if the user_id is allowed to edit or remove this group """
        # only owners can edit or remove groups
        assert self.parent is not None
        return str(self.parent.id()) == str(user_id)


class Checklist(BaseElement):
    def __init__(self, group, id):
        super().__init__(db.checklists, parent=group)
        assert type(group) == Group
        if id is None:
            # create a new checklist
            id = db.checklists.insert_one({'_parentid': group.id()}).inserted_id

        new_info = db.checklists.find_one({'_id': id})
        if new_info is None:
            raise Exception('Checklist not found: {}'.format(id))
        self.info.update(new_info)
        self.children_class = Item


class Item(BaseElement):
    def __init__(self, checklist, id):
        super().__init__(db.items, parent=checklist)
        assert type(checklist) == Checklist
        if id is None:
            # create a new checklist
            id = db.items.insert_one({'_parentid': checklist.id()}).inserted_id

        new_info = db.items.find_one({'_id': id})
        if new_info is None:
            raise Exception('Item not found: {}'.format(id))
        self.info.update(new_info)


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
        return db.groups.find({'_parentid': user_id, 'private': False}, {'name': 1, 'private': 1})
    return db.groups.find({'_parentid': user_id}, {'name': 1, 'private': 1})


def available_checklists(group_id):
    """  Returns: A pymongo.cursor.Cursor with the available checklists in a group """
    if type(group_id) == str:
        try:
            group_id = ObjectId(group_id)
        except InvalidId:
            return []
    return db.checklists.find({'_parentid': group_id}, {'name': 1, '_parentid': 1})


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
    except Exception as exc:
        logger.warn('Something happened constructing the user %s: %s', userid, str(exc))
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
        logger.warn('Group not found: %s', groupid)
        return None
    user = search_user(groupinfo['_parentid'])
    if user is None:
        logger.warn('Group found, but user doesn\'t: %s', groupid)
        return None
    try:
        return Group(user, groupid)
    except Exception as exc:
        logger.warn('Something happened constructing the group %s: %s', groupid, str(exc))
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
    group = search_group(checklistinfo['_parentid'])
    if group is None:
        logger.warn('Checklist found, but group doesn\'t: %s', checklistid)
        return None
    try:
        return Checklist(group, checklistid)
    except Exception as exc:
        logger.warn('Something happened constructing the checklist %s: %s', checklistid, str(exc))
        return None
