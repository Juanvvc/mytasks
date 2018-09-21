import unittest
import flask_testing
import json
import flask
import project.model as model
import project.server.auth
import project.views


def auth_header(userid, password):
    import base64
    authstr = base64.b64encode('{}:{}'.format(userid, password).encode()).decode()
    return 'Basic {}'.format(authstr)


class TestViews(flask_testing.TestCase):
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
        user = model.create_user('USER1', 'PASSWORD1')
        user.create_group({'name': 'GROUP1'})

    def tearDown(self):
        import shutil
        shutil.rmtree(model.DATA_DIR)

    def test_blueprint(self):
        auth = project.server.auth.create_auth()
        self.assertTrue(hasattr(auth, 'login_required'))

        for b in project.views.get_blueprints(auth):
            self.assertTrue(type(b) == flask.Blueprint)

    def test_notlogged(self):
        with self.client:
            response = self.client.get('/0')
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 401)

    def test_baspassword(self):
        with self.client:
            response = self.client.get('/0', headers={'Authorization': auth_header(0, 'BADWOLF')})
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 401)

    def test_logged(self):
        with self.client:
            response = self.client.get('/0', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data['name'], 'USER1')

    def test_404(self):
        with self.client:
            response = self.client.get('/1', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 404)

            response = self.client.get('/XX', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 404)


if __name__ == '__main__':
    unittest.main()
