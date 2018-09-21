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


class TestUsersView(flask_testing.TestCase):
    def create_app(self):
        app = flask.Flask(__name__)
        app.config.from_object('project.server.config.TestingConfig')
        project.model.configure_model(app)
        project.views.register(app)

        @app.errorhandler(400)
        @app.errorhandler(404)
        @app.errorhandler(401)
        def error_handler(error):
            return flask.make_response(flask.jsonify({'error_message': str(error), 'status': error.code}))

        return app

    def setUp(self):
        user = project.model.create_user('USER1', 'PASSWORD1')
        user.create_group({'name': 'GROUP1'})

    def tearDown(self):
        import shutil
        shutil.rmtree(project.model.DATA_DIR)

    def test_availableusers(self):
        with self.client:
            response = self.client.get('/', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertTrue(type(data) == list)
            self.assertTrue(len(data) == 1)
            self.assertTrue('name' in data[0] and data[0]['name'] == 'USER1')

    def test_oneuser(self):
        with self.client:
            response = self.client.get('/0', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'USER1')


if __name__ == '__main__':
    unittest.main()
