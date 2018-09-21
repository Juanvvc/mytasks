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


class TestChecklistsView(flask_testing.TestCase):
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
        group2.create_checklist({'name': 'CHECKLIST1'})
        group2.create_checklist({'name': 'CHECKLIST2'})

    def tearDown(self):
        import shutil
        shutil.rmtree(project.model.DATA_DIR)

    def test_availablechecklists(self):
        with self.client:
            response = self.client.get('/0/groups/1', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            checklists = data.get('checklists', [])
            self.assertTrue(type(checklists) == list)
            self.assertTrue(len(checklists) == 2)
            self.assertTrue('name' in checklists[0] and checklists[0].get('name', '') in ('CHECKLIST1', 'CHECKLIST2'))

    def test_onechecklist(self):
        with self.client:
            response = self.client.get('/0/groups/1/checklists/0', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'CHECKLIST1')

    def test_newchecklist(self):
        """ Test creation of chcklist, and its errors """
        with self.client:
            # try to create a user without information
            response = self.client.post('/0/groups/0/checklists/', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 400)

            # create a checklist
            response = self.client.post('/0/groups/0/checklists/', data=json.dumps(dict(name='NEWNAME')), content_type='application/json', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'NEWNAME')

    def test_updatechecklist(self):
        """ Test to update a checklist, and its errors """
        with self.client:
            # try to update a user without information
            response = self.client.put('/0/groups/1/checklists/0', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 400)

            # update a checklist
            response = self.client.put('/0/groups/1/checklists/0', data=json.dumps(dict(name='NEWNAME2')), content_type='application/json', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'NEWNAME2')

    def test_deletechecklist(self):
        """ Test deleting a checklist, and its errors """
        with self.client:
            response = self.client.delete('/0/groups/1/checklists/0', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 200)
            response = self.client.get('/0/groups/1/checklists/0', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 404)

            # non existing checklist
            response = self.client.delete('/0/groups/999/checklists/999', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 404)


if __name__ == '__main__':
    unittest.main()
