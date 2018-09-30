import unittest
import flask
import flask_testing
import project.model
import project.views
from project.tests import HTTPHelper


class TestGroupsView(flask_testing.TestCase):
    def create_app(self):
        app = flask.Flask(__name__)
        app.config.from_object('project.server.config.TestingConfig')
        project.model.configure_model(app)
        project.views.register(app)

        @app.errorhandler(400)
        @app.errorhandler(404)
        @app.errorhandler(401)
        @app.errorhandler(500)
        def error_handler(error):
            return flask.make_response(flask.jsonify({'error_message': str(error), 'status': error.code}))

        return app

    def setUp(self):
        self.user = project.model.create_user('USER1', 'PASSWORD1')
        self.group1 = self.user.create_child({'name': 'GROUP1', 'private': True})
        self.group2 = self.user.create_child({'name': 'GROUP2', 'private': False})
        self.group2.create_child({'name': 'NEWCHECKLIST'})

        self.user2 = project.model.create_user('USER2', 'PASSWORD2')

    def tearDown(self):
        project.model.db.command('dropDatabase')

    def test_availablegroups(self):
        " Test a user can access to a list with the groups owned by him, but not to the private groups of other users"
        with self.client:
            url = flask.url_for('users.info', _id=str(self.user.id()))
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])

            # user1 gets a list with both groups
            data = http.get(url)
            groups = data.get('groups', [])
            self.assertTrue(type(groups) == list)
            self.assertEqual(len(groups), 2)
            self.assertTrue('name' in groups[0] and groups[0].get('name', '') in ('GROUP1', 'GROUP2'))
            self.assertTrue('name' in groups[1] and groups[1].get('name', '') in ('GROUP1', 'GROUP2'))

            # user2 only gets public groups
            data = http.get(url, auth=['USER2', 'PASSWORD2'])
            groups = data.get('groups', [])
            self.assertTrue(type(groups) == list)
            self.assertEqual(len(groups), 1)
            self.assertFalse(groups[0]['private'])
            self.assertEqual(groups[0]['name'], 'GROUP2')

    def test_onegroup(self):
        " Test a user can access to his groups, but not to a private group owned by other user"
        with self.client:
            # user1 can access to group1
            url = flask.url_for('groups.info', _id=str(self.group1.id()))
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])
            data = http.get(url)
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data)
            self.assertTrue(data['name'] == 'GROUP1')

            # user2 cannot access to group1
            data = http.get(url, auth=['USER2', 'PASSWORD2'])
            self.assertTrue('error_message' in data)
            self.assertEqual(data['status'], 401)

            # user2 can access group2
            url = flask.url_for('groups.info', _id=str(self.group2.id()))
            data = http.get(url, auth=['USER2', 'PASSWORD2'])
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data)
            self.assertTrue(data['name'] == 'GROUP2')

    def test_newgroup(self):
        """ Test creation of group, and its errors """
        with self.client:
            url = flask.url_for('groups.new')
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])

            # try to create a group without information
            data = http.post(url)
            self.assertEqual(data.get('status', 0), 400)

            # create a group
            data = http.post(url, data=dict(name='NEWNAME'))
            self.assertFalse('error_message' in data)
            self.assertTrue(data.get('name', None), 'NEWNAME')
            # check the default value is "private group"
            self.assertTrue(data.get('private'), True)

    def test_updategroup(self):
        """ Test to update a group, and its errors """
        with self.client:
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])
            # try to update a group without information
            url = flask.url_for('groups.info', _id=str(self.group2.id()))
            data = http.put(url)
            self.assertEqual(data.get('status', 0), 400)

            # update a group
            data = http.put(url, data=dict(name='NEWNAME'))
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'NEWNAME')

            # user 2 cannot update groups owned by user1, public or private
            url = flask.url_for('groups.info', _id=str(self.group2.id()))
            data = http.put(url, data=dict(name='NEWNAME2'), auth=['USER2', 'PASSWORD2'])
            self.assertTrue('error_message' in data)
            url = flask.url_for('groups.info', _id=str(self.group1.id()))
            data = http.put(url, data=dict(name='NEWNAME2'), auth=['USER2', 'PASSWORD2'])
            self.assertTrue('error_message' in data)

    def test_deletegroup(self):
        """ Test to delete a group, and its errors"""
        with self.client:
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])

            # user 2 cannot delete groups owned by user1, public or private
            url = flask.url_for('groups.info', _id=str(self.group1.id()))
            data = http.delete(url, auth=['USER2', 'PASSWORD2'])
            self.assertTrue('error_message' in data)
            url = flask.url_for('groups.info', _id=str(self.group2.id()))
            data = http.delete(url, auth=['USER2', 'PASSWORD2'])
            self.assertTrue('error_message' in data)

            # user 1 can delete group1, which is empty
            url = flask.url_for('groups.info', _id=str(self.group1.id()))
            data = http.delete(url)
            self.assertEqual(data.get('status', 0), 200)
            data = http.get(url)
            self.assertEqual(data.get('status', 0), 404)

            # non empty group: check it exists, try to delete, check it still exists
            ck = project.model.db.checklists.find_one({'_parentid': self.group2.id()})
            self.assertFalse(ck is None)
            url = flask.url_for('groups.info', _id=str(self.group2.id()))
            data = http.get(url)
            self.assertEqual(data.get('status', 0), 0)
            data = http.delete(url)
            self.assertEqual(data.get('status', 0), 401)
            data = http.get(url)
            self.assertEqual(data.get('status', 0), 0)

            # unexisting group
            url = flask.url_for('groups.info', _id='XXX')
            data = http.delete(url)
            self.assertEqual(data.get('status', 0), 404)


if __name__ == '__main__':
    unittest.main()
