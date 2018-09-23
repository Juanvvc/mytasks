import unittest
import flask
import flask_testing
import json
import project.model
import project.views


def auth_header(userid, password):
    import base64
    authstr = base64.b64encode('{}:{}'.format(userid, password).encode()).decode()
    return 'Basic {}'.format(authstr)


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
        self.group1 = self.user.create_group({'name': 'GROUP1', 'private': True})
        self.group2 = self.user.create_group({'name': 'GROUP2', 'private': False})
        self.group2.create_checklist({'name': 'NEWCHECKLIST'})

        self.user2 = project.model.create_user('USER2', 'PASSWORD2')

    def tearDown(self):
        project.model.db.command('dropDatabase')

    def test_availablegroups(self):
        " Test a user can access to a list with the groups owned by him, but not to the private groups of other users"
        with self.client:
            url = flask.url_for('users.info', user_id=str(self.user.id()))

            # user1 gets a list with both groups
            response = self.client.get(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            groups = data.get('groups', [])
            self.assertTrue(type(groups) == list)
            self.assertEqual(len(groups), 2)
            self.assertTrue('name' in groups[0] and groups[0].get('name', '') in ('GROUP1', 'GROUP2'))
            self.assertTrue('name' in groups[1] and groups[1].get('name', '') in ('GROUP1', 'GROUP2'))

            # user2 only gets public groups
            response = self.client.get(url, headers={'Authorization': auth_header('USER2', 'PASSWORD2')})
            data = json.loads(response.data.decode())
            groups = data.get('groups', [])
            self.assertTrue(type(groups) == list)
            self.assertEqual(len(groups), 1)
            self.assertFalse(groups[0]['private'])
            self.assertEqual(groups[0]['name'], 'GROUP2')

    def test_onegroup(self):
        " Test a user can access to his groups, but not to a private group owned by other user"
        with self.client:
            # user1 can access to group1
            url = flask.url_for('groups.info', group_id=str(self.group1.id()))
            response = self.client.get(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data)
            self.assertTrue(data['name'] == 'GROUP1')

            # user2 cannot access to group1
            url = flask.url_for('groups.info', group_id=str(self.group1.id()))
            response = self.client.get(url, headers={'Authorization': auth_header('USER2', 'PASSWORD2')})
            data = json.loads(response.data.decode())
            self.assertTrue('error_message' in data)
            self.assertEqual(data['status'], 401)

            # user2 can access group2
            url = flask.url_for('groups.info', group_id=str(self.group2.id()))
            response = self.client.get(url, headers={'Authorization': auth_header('USER2', 'PASSWORD2')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data)
            self.assertTrue(data['name'] == 'GROUP2')

    def test_newgroup(self):
        """ Test creation of group, and its errors """
        with self.client:
            url = flask.url_for('groups.new', user_id=str(self.user.id()))

            # try to create a user without information
            response = self.client.post(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 400)

            # create a checklist
            response = self.client.post(url, data=json.dumps(dict(name='NEWNAME')), content_type='application/json', headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'NEWNAME')

    def test_updategroup(self):
        """ Test to update a group, and its errores """
        with self.client:
            # try to update a group without information
            url = flask.url_for('groups.info', user_id=str(self.user.id()), group_id=str(self.group2.id()))
            response = self.client.post(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 400)

            # update a group
            response = self.client.post(url, data=json.dumps(dict(name='NEWNAME')), content_type='application/json', headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'NEWNAME')

            # user 2 cannot update groups owned by user1, public or private
            url = flask.url_for('groups.info', user_id=str(self.user.id()), group_id=str(self.group2.id()))
            response = self.client.post(url, data=json.dumps(dict(name='NEWNAME')), content_type='application/json', headers={'Authorization': auth_header('USER2', 'PASSWORD2')})
            data = json.loads(response.data.decode())
            self.assertTrue('error_message' in data)
            url = flask.url_for('groups.info', user_id=str(self.user.id()), group_id=str(self.group1.id()))
            response = self.client.post(url, data=json.dumps(dict(name='NEWNAME')), content_type='application/json', headers={'Authorization': auth_header('USER2', 'PASSWORD2')})
            data = json.loads(response.data.decode())
            self.assertTrue('error_message' in data)

    def test_deletegroup(self):
        """ Test to delete a group, and its errors"""
        with self.client:
            # user 2 cannot delete groups owned by user1, public or private
            url = flask.url_for('groups.info', user_id=str(self.user.id()), group_id=str(self.group2.id()))
            response = self.client.delete(url, data=json.dumps(dict(name='NEWNAME')), content_type='application/json', headers={'Authorization': auth_header('USER2', 'PASSWORD2')})
            data = json.loads(response.data.decode())
            self.assertTrue('error_message' in data)
            url = flask.url_for('groups.info', user_id=str(self.user.id()), group_id=str(self.group1.id()))
            response = self.client.delete(url, data=json.dumps(dict(name='NEWNAME')), content_type='application/json', headers={'Authorization': auth_header('USER2', 'PASSWORD2')})
            data = json.loads(response.data.decode())
            self.assertTrue('error_message' in data)

            # user 1 can delete group1, which is empty
            url = flask.url_for('groups.info', user_id=str(self.user.id()), group_id=str(self.group1.id()))
            response = self.client.delete(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 200)
            response = self.client.get(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 404)

            # non empty group: check it exists, try to delete, check it still exists
            url = flask.url_for('groups.info', user_id=str(self.user.id()), group_id=str(self.group2.id()))
            response = self.client.get(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 0)
            response = self.client.delete(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 500)
            response = self.client.get(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 0)

            # unexisting group
            url = flask.url_for('groups.info', user_id=str(self.user.id()), group_id='XXX')
            response = self.client.delete(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 404)


if __name__ == '__main__':
    unittest.main()
