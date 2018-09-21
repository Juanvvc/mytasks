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
        user = project.model.create_user('USER1', 'PASSWORD1')
        user.create_group({'name': 'GROUP1'})
        group2 = user.create_group({'name': 'GROUP2'})
        group2.create_checklist({'name': 'NEWCHECKLIST'})

    def tearDown(self):
        import shutil
        shutil.rmtree(project.model.DATA_DIR)

    def test_availablegroups(self):
        with self.client:
            response = self.client.get('/0', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            groups = data.get('groups', [])
            self.assertTrue(type(groups) == list)
            self.assertTrue(len(groups) == 2)
            self.assertTrue('name' in groups[0] and groups[0].get('name', '') in ('GROUP1', 'GROUP2'))
            self.assertTrue('name' in groups[1] and groups[1].get('name', '') in ('GROUP1', 'GROUP2'))

    def test_onegroup(self):
        with self.client:
            response = self.client.get('/0/groups/0', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data)
            self.assertTrue(data['name'] == 'GROUP1')

    def test_newgroup(self):
        """ Test creation of group, and its errors """
        with self.client:
            # try to create a user without information
            response = self.client.post('/0/groups/', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 400)

            # create a checklist
            response = self.client.post('/0/groups/', data=json.dumps(dict(name='NEWNAME')), content_type='application/json', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'NEWNAME')

    def test_updategroup(self):
        """ Test to update a group, and its errores """
        with self.client:
            # try to update a group without information
            response = self.client.post('/0/groups/0', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 400)

            # update a group
            response = self.client.post('/0/groups/0', data=json.dumps(dict(name='NEWNAME')), content_type='application/json', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'NEWNAME')

    def test_deletegroup(self):
        """ Test to delete a group, and its errors"""
        with self.client:
            # existing group
            response = self.client.delete('/0/groups/0', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 200)
            response = self.client.get('/0/groups/0', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 404)

            # non empty group: check it exists, try to delete, check it still exists
            response = self.client.get('/0/groups/1', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 0)
            response = self.client.delete('/0/groups/1', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 500)
            response = self.client.get('/0/groups/1', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 0)

            # unexisting group
            response = self.client.delete('/0/groups/999', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 404)


if __name__ == '__main__':
    unittest.main()
