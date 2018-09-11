from project.server import app
import project.model as model
import unittest
import shutil
import os


class TestModel(unittest.TestCase):
    def setUp(self):
        data_dir = app.config.get('DATA_DIR')
        # Create file structure. We cannot use model.User.create* because we are testing those files!

        # create a user 0
        os.makedirs(os.path.join(data_dir, '0'), exist_ok=False)
        os.mknod(os.path.join(data_dir, '0', model.METADATA_FILE))
        # create a directory 0 for user 0 (it is not a group because medata is not created)
        os.makedirs(os.path.join(data_dir, '0', '0'), exist_ok=False)
        # create a directory 1 for user 0. It is a group
        os.makedirs(os.path.join(data_dir, '0', '1'), exist_ok=False)
        os.mknod(os.path.join(data_dir, '0', '1', model.METADATA_FILE))
        # create a checklist 5 in group 1
        os.mknod(os.path.join(data_dir, '0', '1', '5.json'))

        # create a directory 1. It is not a user
        os.makedirs(os.path.join(data_dir, '1'), exist_ok=False)

        # create a user 2 with an empty group
        os.makedirs(os.path.join(data_dir, '2'), exist_ok=False)
        os.mknod(os.path.join(data_dir, '2', model.METADATA_FILE))

        # create a directory 3. It is not a user
        os.makedirs(os.path.join(data_dir, '3'), exist_ok=False)

    def tearDown(self):
        shutil.rmtree(app.config.get('DATA_DIR'))
        pass

    def test_users(self):
        " Test only users 0 and 2 exist. "
        self.assertEqual(sorted(model.available_users()), [0, 2])

    def test_search_user(self):
        "Test if a user can be found usigs its userid"
        user = model.search_user(0)
        self.assertTrue(type(user) == model.User and user.id == 0)

    def test_search_username(self):
        "Test if a user can be found usigs its username"
        model.create_user('NEWUSER')
        results = model.search_username('NEWUSER')
        self.assertTrue(len(results) == 1)
        self.assertTrue(results[0].info.get('name', None) == 'NEWUSER')

    def test_user_create(self):
        " test a user can be created "
        new_user = model.create_user('NEWUSER')
        self.assertEqual(type(new_user), model.User)
        self.assertEqual(new_user.id, 3)
        self.assertEqual(new_user.info['name'], 'NEWUSER')
        # check the new user cannot login
        self.assertFalse(model.PASSWORD_FIELDNAME in new_user.info)

    def test_user_create2(self):
        " Remove all users and create a new one with id 0 "
        for u in model.available_users():
            user = model.search_user(u)
            user.delete()
        new_user = model.create_user('NEWUSER')
        self.assertEqual(type(new_user), model.User)
        self.assertEqual(new_user.id, 0)

    def test_user_create3(self):
        " Create a new user with a password. Check a good and a bad password "
        new_user = model.create_user('NEWUSER', 'PASSWORD')
        self.assertEqual(type(new_user), model.User)
        self.assertTrue(model.PASSWORD_FIELDNAME in new_user.info)
        self.assertTrue(new_user.verify_password('PASSWORD'))
        self.assertFalse(new_user.verify_password('WRONG'))

    def test_remove_user(self):
        " Remove user 2 and test only user 0 exist. "
        self.assertTrue(model.search_user(2).delete())
        self.assertEqual(sorted(model.available_users()), [0])

    def test_edit_user(self):
        " Change the name of user 0 "
        user = model.search_user(0)
        user.info['name'] = 'Jhon'
        self.assertTrue(user.save())

        new_user = model.search_user(0)
        self.assertEqual(new_user.info['name'], 'Jhon')

    def test_groups_0(self):
        " Test user 0 only has group 1 "
        self.assertEqual(sorted(model.available_groups(0)), [1])

    def test_groups_123(self):
        " Test unexisting user returns empty groups "
        self.assertEqual(model.available_groups(123), [])
        self.assertEqual(model.search_group(123, 0), None)

    def test_group_create(self):
        " Test groups can be created."
        # User 2 has no groups. A new group will be created as 0.
        user = model.search_user(2)
        self.assertEqual(type(user), model.User)
        group = user.create_group()
        self.assertEqual(type(group), model.Group)
        self.assertEqual(group.id, 0)

        # User 0 has a group 1. A new group will be created as 2.
        user = model.search_user(0)
        self.assertEqual(type(user), model.User)
        group = user.create_group()
        self.assertEqual(group.id, 2)

    def test_group_edit(self):
        " Change the name of a group "
        group = model.search_group(0, 1)
        group.info['name'] = 'GROUP'
        self.assertTrue(group.save())

        new_group = model.search_group(0, 1)
        self.assertEqual(new_group.info['name'], 'GROUP')

    def test_group_delete(self):
        " Test delete a non empty group "
        group = model.search_group(0, 1)
        self.assertFalse(group.delete())
        self.assertEqual(model.available_groups(0), [1])

    def test_group_delete2(self):
        " Test delete an empty group "
        user = model.search_user(2)
        group = user.create_group()
        self.assertEqual(len(model.available_groups(2)), 1)
        self.assertTrue(group.delete())
        self.assertEqual(len(model.available_groups(2)), 0)

    def test_checklists_0(self):
        " Test user 0 group 1 has a checklist 5 "
        self.assertEqual(sorted(model.available_checklists(0, 1)), [5])
        self.assertEqual(type(model.search_checklist(0, 1, 5)), model.Checklist)

    def test_checklist_create(self):
        """ Test groups can be created.

        User 0 has a group 1 with checklist 5. A new checklist will be created.
        """
        group = model.search_group(0, 1)
        checklist = group.create_checklist()
        self.assertEqual(type(checklist), model.Checklist)
        self.assertEqual(checklist.id, 6)

    def test_checklists_edit(self):
        " Change the name of a checklist "
        checklist = model.search_checklist(0, 1, 5)
        checklist.info['name'] = 'CK'
        self.assertTrue(checklist.save())

        new_checklist = model.search_checklist(0, 1, 5)
        self.assertEqual(new_checklist.info['name'], 'CK')

    def test_checklist_delete(self):
        " Delete a checklist "
        checklist = model.search_checklist(0, 1, 5)
        self.assertTrue(checklist.delete())
        self.assertEqual(model.available_checklists(0, 1), [])


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.CRITICAL)
    unittest.main()
