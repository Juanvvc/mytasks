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
    def __init__(self, _id, collection=None, parent_class=None, children_class=None):
        """

        Args:
            collection: a db.COLLECTION for this element
            parent_class: The BaseElement which contains this one, if any
            children_class: The BaseElement this element can contain, if any
        """
        self.info = dict(_id=_id)
        self._collection = collection
        self._parent_class = parent_class
        self._children_class = children_class

    def id(self):
        """ A convenience method to get the bson.objectid.ObjectId of this element """
        _id = self.info.get('_id', None)
        if '_id' is None:
            raise Exception('Somehow, the element has no identifier')
        assert type(_id) == ObjectId
        return _id

    def summary(self):
        """ Returns the summary of the element.

        This method shouldn't return any dangerous information: passwords, hashes of passwords...
        Only data intented that can be publicly accessed is returned. """

        return dict(
            _id=str(self.id()),
            name=self.info.get('name', ''),
            _parentid=self.info.get('_parentid', None)
        )

    def sane_info(self):
        """ Returns an info object that can be serialized """
        new_info = self.info.copy()
        if '_id' in new_info:
            new_info['_id'] = str(new_info['_id'])
        if '_parentid' in new_info:
            new_info['_parentid'] = str(new_info['_parentid'])
        return new_info

    def save(self):
        # before saving, make sure the identifiers are really identifiers
        try:
            if type(self.info['_id']) != ObjectId:
                self.info['_id'] = ObjectId(self.info['_id'])
            if '_parentid' in self.info and type(self.info['_parentid']) != ObjectId:
                self.info['_parentid'] = ObjectId(self.info['_parentid'])
        except InvalidId:
            return False
        self._collection.save(self.info)
        return True

    def visible_by(self, user_id):
        """ Returns True if user_id is allowed to access the BaseElement """
        if self.info.get('_parentid') is not None:
            return self.parent().visible_by(user_id)
        return True

    def editable_by(self, user_id):
        """ Returns True if the user_id is allowed to edit or remove this BaseElement """
        if self.info.get('_parentid') is not None:
            return self.parent().editable_by(user_id)
        return True

    def delete(self):
        self._collection.remove({'_id': self.id()})
        return True

    def create_child(self, info):
        """ Creates a new chil in this element

        If info includes an _id or a _parentid, it is ignored
        """
        if self._children_class is None:
            raise Exception('This element type cannot have children')
        new_child = self._children_class(None)

        # ignore these fields, if exist
        new_info = info.copy()
        new_info.pop('_id', None)
        new_info.pop('_parentid', None)

        # update the info and save
        new_child.info.update(new_info)
        new_child.info.update({'_parentid': self.id()})
        new_child.save()
        return new_child

    def parent(self, use_cached=True):
        """ Returns a BaseElement with the parent, if anyself.

        This method caches the first call to avoid requests to the database """
        if use_cached and hasattr(self, '_parent') and self._parent is not None:
            return self._parent
        if '_parentid' not in self.info or not hasattr(self, '_parent_class'):
            return None
        return search_element(self._parent_class, self.info.get('_parentid'))


class User(BaseElement):
    def __init__(self, _id):
        super().__init__(_id, collection=db.users, children_class=Group)
        if _id is None:
            # create a new user
            _id = db.users.insert_one({}).inserted_id

        new_info = db.users.find_one({'_id': _id})
        if new_info is None:
            raise Exception('User not found: {}'.format(_id))
        self.info.update(new_info)

    def hash_password(self, password):
        """ Save a password hash in the user.

        Args:
            password (str): the password of the user. Only it hash is saved.
        """
        self.info[PASSWORD_FIELDNAME] = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password):
        """ Returns True if the password is verified.

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
    def __init__(self, _id):
        super().__init__(_id, collection=db.groups, children_class=Checklist, parent_class=User)
        if _id is None:
            # create a new group
            _id = db.groups.insert_one({'private': True}).inserted_id

        new_info = db.groups.find_one({'_id': _id})
        if new_info is None:
            raise Exception('Group not found: {}'.format(_id))
        self.info.update(new_info)

    def summary(self):
        return super().summary().update({'private': self.info.get('private', True)})

    def visible_by(self, user_id):
        """ Returns True if user_id is allowed to access the group """
        my_user = self.parent()
        assert my_user is not None
        # a user can access its own groups always
        if str(user_id) == str(my_user.id()):
            return True
        # a different user can access only to non private groups
        return not self.info.get('private', True)

    def editable_by(self, user_id):
        """ Returns True if the user_id is allowed to edit or remove this group """
        # only owners can edit or remove groups
        my_user = self.parent()
        assert my_user is not None
        return str(my_user.id()) == str(user_id)


class Checklist(BaseElement):
    def __init__(self, _id):
        super().__init__(_id, collection=db.checklists, parent_class=Group, children_class=Item)
        if _id is None:
            # create a new checklist
            _id = db.checklists.insert_one({}).inserted_id

        new_info = db.checklists.find_one({'_id': _id})
        if new_info is None:
            raise Exception('Checklist not found: {}'.format(_id))
        self.info.update(new_info)

    def delete_child(self, item_id):
        if 'items' not in self.info:
            return False
        item_pos = -1
        for i in range(0, len(self.info['items'])):
            if str(self.info['items'][i]['_id']) == str(item_id):
                item_pos = i
                break
        if item_pos == -1:
            return False
        self.info['items'].pop(item_pos)
        return self.save()

    def create_child(self, info):
        child = super().create_child(info)
        if 'items' not in self.info:
            self.info['items'] = list([dict(_id=child.id())])
        else:
            self.info['items'].append(dict(_id=child.id()))
        self.save()
        return child


class Item(BaseElement):
    def __init__(self, _id):
        super().__init__(_id, collection=db.items, parent_class=Checklist)
        if _id is None:
            # create a new checklist
            _id = db.items.insert_one({}).inserted_id

        new_info = db.items.find_one({'_id': _id})
        if new_info is None:
            raise Exception('Item not found: {}'.format(_id))
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
    return db.checklists.find({'_parentid': group_id}, {'name': 1, '_order': 1, '_parentid': 1}).sort('_order', pymongo.DESCENDING)


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


def search_element(element_class, element_id):
    """ Search for a generic element

    Attr:
        element_class: the class of the element to search. Currently: User, Group, Checklist, Item
        element_id: the identifier of the element to search

    Returns:
        The element, or None if it doesn't exist.
    """
    if type(element_id) == str:
        try:
            element_id = ObjectId(element_id)
        except InvalidId:
            logger.warn('Invalid Identifier: %s', element_id)
            return None
    try:
        return element_class(element_id)
    except Exception as exc:
        return None


def search_username(name):
    """ Gets a user by its username, if exists.

    Args:
        user_id (int): The identifier of the user

    Returns:
        The User, or None if it doesn't exist.
    """
    userinfo = db.users.find_one({'name': name})
    if userinfo is None:
        logger.warn('User not found: %s', name)
        return None
    return User(userinfo['_id'])
