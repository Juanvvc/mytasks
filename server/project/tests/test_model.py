import project.model as model
import unittest
from bson.objectid import ObjectId


def cursor_size(cursor):
    """ Returns the size of a pymongo.Cursor """
    size = 0
    for c in cursor:
        size += 1
    return size


class TestModel(unittest.TestCase):
    def setUp(self):
        # create a user 0
        self.user0 = model.db.users.insert({'name': 'NAME0'})
        self.group0 = model.db.groups.insert({'name': 'GROUP0', 'parentid': self.user0, 'private': True})
        self.checklist0 = model.db.checklists.insert({'name': 'CHECKLIST0', 'parentid': self.group0})
        self.group1 = model.db.groups.insert({'name': 'GROUP1', 'parentid': self.user0, 'private': False})
        self.checklist1 = model.db.checklists.insert({'name': 'CHECKLIST0', 'parentid': self.group1})

        # create user 1
        self.user1 = model.db.users.insert({'name': 'NAME1'})
        self.group11 = model.db.groups.insert({'name': 'GROUP1', 'parentid': self.user1})

    def tearDown(self):
        model.db.command('dropDatabase')

    def test_users(self):
        " Test there are two users int he database. "
        self.assertEqual(cursor_size(model.available_users()), 2)

    def test_search_user(self):
        "Test if a user can be found using its parentid"
        user = model.User(self.user0)
        self.assertEqual(type(user), model.User)
        self.assertEqual(user.info['name'], 'NAME0')

        user = model.search_element(model.User, self.user0)
        self.assertEqual(type(user), model.User)
        self.assertEqual(user.info['name'], 'NAME0')

    def test_search_username(self):
        "Test if a user can be found usigs its username"
        user = model.search_username('NAME0')
        self.assertEqual(type(user), model.User)
        self.assertEqual(user.info['_id'], self.user0)

    def test_search_unexisting_user(self):
        " Test you cannot search for unexisting users "
        self.assertRaises(Exception, model.User, ObjectId('1234567890ab1234567890ab'))
        self.assertEquals(model.search_username('NOEXISTS'), None)

    def test_user_create(self):
        " test a user can be created "
        new_user = model.create_user('NEWUSER')
        self.assertEqual(type(new_user), model.User)
        self.assertEqual(new_user.info['name'], 'NEWUSER')
        # check the new user cannot login
        self.assertFalse(model.PASSWORD_FIELDNAME in new_user.info)

    def test_user_create2(self):
        " Create a new user with a password. Check a good and a bad password "
        new_user = model.create_user('NEWUSER', 'PASSWORD')
        self.assertEqual(type(new_user), model.User)
        self.assertTrue(model.PASSWORD_FIELDNAME in new_user.info)
        self.assertTrue(new_user.verify_password('PASSWORD'))
        self.assertFalse(new_user.verify_password('WRONG'))

    def test_remove_user(self):
        " Remove user 2 and test only user 0 exist. "
        model.User(self.user0).delete()
        self.assertEqual(cursor_size(model.available_users()), 1)

    def test_edit_user(self):
        " Change the name of user0 "
        user = model.User(self.user0)
        user.info['name'] = 'John'
        self.assertTrue(user.save())

        new_user = model.User(self.user0)
        self.assertEqual(new_user.info['_id'], self.user0)
        self.assertEqual(new_user.info['name'], 'John')

    def test_groups_0(self):
        " Test groups in user0 "
        # check the number of groups
        self.assertEqual(cursor_size(model.available_groups(self.user0)), 2)

    def test_groups_123(self):
        " Test unexisting user returns empty groups "
        self.assertEqual(cursor_size(model.available_groups(ObjectId('1234567890ab1234567890ab'))), 0)

    def test_group_create(self):
        " Test groups can be created."
        # User 2 has no groups. A new group will be created as 0.
        user = model.User(self.user1)
        group = user.create_child({'name': 'NEW_GROUP', 'parentid': 'XXX'})

        group_new = model.search_element(model.Group, group.id())
        self.assertEqual(type(group_new), model.Group)
        self.assertTrue('name' in group_new.info)
        self.assertTrue(group_new.info.get('name', None) == 'NEW_GROUP')

        # check private is the dedault option
        self.assertTrue('private' in group_new.info)
        self.assertTrue(group_new.info['private'])

        # finaly, assert the new group has the right parentid and not XXX
        self.assertEqual(group_new.parent().id(), self.user1)

    def test_group_edit(self):
        " Change the name of a group "
        group = model.search_element(model.Group, self.group0)
        group.info['name'] = 'GROUPNEW'
        self.assertTrue(group.save())

        new_group = model.search_element(model.Group, self.group0)
        self.assertEqual(new_group.info['name'], 'GROUPNEW')

    def test_group_delete(self):
        " Test delete an empty group "
        group = model.search_element(model.Group, self.group11)
        self.assertFalse(group is None)
        self.assertTrue(group.delete())
        self.assertTrue(model.search_element(model.Group, self.group11) is None)

    def test_checklist_create(self):
        """ Test checklists can be created.  """
        group = model.search_element(model.Group, self.group0)
        self.assertFalse(group is None)
        checklist = group.create_child({'name': 'CK', 'parentid': 'XXX'})
        self.assertEqual(type(checklist), model.Checklist)
        self.assertTrue('name' in checklist.info)
        self.assertTrue(checklist.info.get('name', None) == 'CK')

        # finaly, assert the new checklist has the right parentid and not XXX
        self.assertEqual(checklist.info.get('parentid', ''), self.group0)

    def test_checklists_permissions(self):
        """ Test permissions """

        # user1 cannot view or edit a checklist in a private group
        checklist = model.search_element(model.Checklist, self.checklist0)
        self.assertFalse(checklist.visible_by(self.user1))
        self.assertFalse(checklist.editable_by(self.user1))

        # user1 can view but not edit a checklist ina public group
        checklist = model.search_element(model.Checklist, self.checklist1)
        self.assertFalse(checklist.parent().info.get('private', False))
        self.assertTrue(checklist.visible_by(self.user1))
        self.assertFalse(checklist.editable_by(self.user1))

    def test_checklists_edit(self):
        " Change the name of a checklist "
        checklist = model.search_element(model.Checklist, self.checklist0)
        self.assertFalse(checklist is None)
        checklist.info['name'] = 'CKNEW'
        self.assertTrue(checklist.save())

        checklist = model.search_element(model.Checklist, self.checklist0)
        self.assertEqual(checklist.info['name'], 'CKNEW')

    def test_checklist_delete(self):
        " Delete a checklist "
        checklist = model.search_element(model.Checklist, self.checklist0)
        self.assertFalse(checklist is None)
        self.assertTrue(checklist.delete())
        checklist = model.search_element(model.Checklist, self.checklist0)
        self.assertTrue(checklist is None)
