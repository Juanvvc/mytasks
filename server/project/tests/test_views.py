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
        self.user = model.create_user('USER1', 'PASSWORD1')
        self.user.create_group({'name': 'GROUP1'})

    def tearDown(self):
        project.model.db.command('dropDatabase')

    def test_blueprint(self):
        auth = project.server.auth.create_auth()
        self.assertTrue(hasattr(auth, 'login_required'))

        for b in project.views.get_blueprints(auth):
            self.assertTrue(type(b) == flask.Blueprint)

    def test_notlogged(self):
        with self.client:
            url = flask.url_for('users.info', user_id=str(self.user.id()))
            response = self.client.get(url)
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 401)

    def test_baspassword(self):
        " Try to log with a bad password "
        with self.client:
            url = flask.url_for('users.info', user_id=str(self.user.id()))
            response = self.client.get(url, headers={'Authorization': auth_header('USER1', 'BADWOLF')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 401)

    def test_logged(self):
        " Log with a good password "
        with self.client:
            url = flask.url_for('users.info', user_id=str(self.user.id()))
            response = self.client.get(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertFalse('error_message' in data)
            self.assertEqual(data.get('name', ''), 'USER1')

    def test_token(self):
        " Get a token and authenticate with the token "
        with self.client:
            # get the token
            url = flask.url_for('users.login')
            response = self.client.get(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 200)
            self.assertNotEqual(data.get('token', ''), '')
            # test the token
            token = data['token']
            url = flask.url_for('users.info', user_id=str(self.user.id()))
            response = self.client.get(url, headers={'Authorization': auth_header(token, '')})
            data = json.loads(response.data.decode())
            self.assertTrue('error_message' not in data)
            self.assertEqual(data.get('name', ''), 'USER1')
            self.assertEqual(flask.g.user_id, str(self.user.id()))

    def test_404(self):
        with self.client:
            # valid ObjectID
            url = flask.url_for('users.info', user_id='1234567890ab1234567890ab')
            response = self.client.get(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 404)

            # Not valid ObjectId
            url = flask.url_for('users.info', user_id='XX')
            response = self.client.get(url, headers={'Authorization': auth_header('USER1', 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('status', 0), 404)


if __name__ == '__main__':
    unittest.main()
