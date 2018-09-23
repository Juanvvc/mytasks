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
        self.user = project.model.create_user('USER1', 'PASSWORD1')
        self.user.create_group({'name': 'GROUP1'})
        self.group2 = self.user.create_group({'name': 'GROUP2'})
        self.checklist1 = self.group2.create_checklist({'name': 'CHECKLIST1'})
        self.checklist2 = self.group2.create_checklist({'name': 'CHECKLIST2'})

    def tearDown(self):
        project.model.db.command('dropDatabase')

    def test_availablechecklists(self):
        with self.client:
            url = flask.url_for('groups.info', user_id=self.user.id(), group_id=self.group2.id())
            response = self.client.get(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            checklists = data.get('checklists', [])
            self.assertTrue(type(checklists) == list)
            self.assertEqual(len(checklists), 2)
            self.assertTrue('name' in checklists[0] and checklists[0].get('name', '') in ('CHECKLIST1', 'CHECKLIST2'))

    def test_onechecklist(self):
        with self.client:
            url = flask.url_for('checklists.info', user_id=self.user.id(), group_id=self.group2.id(), checklist_id=self.checklist1.id())

            response = self.client.get(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'CHECKLIST1')

    def test_newchecklist(self):
        """ Test creation of chcklist, and its errors """
        with self.client:
            url = flask.url_for('checklists.new', user_id=str(self.user.id()), group_id=str(self.group2.id()))

            # try to create a user without information
            response = self.client.post(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 400)

            # create a checklist
            response = self.client.post(url, data=json.dumps(dict(name='NEWNAME')), content_type='application/json', headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'NEWNAME')

    def test_updatechecklist(self):
        """ Test to update a checklist, and its errors """
        with self.client:
            url = flask.url_for('checklists.info', user_id=str(self.user.id()), group_id=str(self.group2.id()), checklist_id=str(self.checklist1.id()))

            # try to update a checklist without information
            response = self.client.put(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 400)

            # update a checklist
            response = self.client.put(url, data=json.dumps(dict(name='NEWNAME2')), content_type='application/json', headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'NEWNAME2')

    def test_deletechecklist(self):
        """ Test deleting a checklist, and its errors """
        with self.client:
            url = flask.url_for('checklists.info', user_id=str(self.user.id()), group_id=str(self.group2.id()), checklist_id=str(self.checklist1.id()))

            response = self.client.delete(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 200)
            response = self.client.get(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 404)

            # non existing checklist
            url = flask.url_for('checklists.info', user_id=str(self.user.id()), group_id=str(self.group2.id()), checklist_id='XXX')
            response = self.client.delete(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 404)


if __name__ == '__main__':
    unittest.main()
