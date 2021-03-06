import unittest
import flask
import flask_testing
import project.model
import project.views
from project.tests import HTTPHelper


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
        self.user = project.model.create_user('USER1', 'PASSWORD1')
        self.user.create_child({'name': 'GROUP1'})

    def tearDown(self):
        project.model.db.command('dropDatabase')

#    def test_availableusers(self):
#        with self.client:
#            url = flask.url_for('users.available')
#            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])
#
#            data = http.get(url)
#            self.assertFalse('error_message' in data)
#            self.assertTrue(type(data) == list)
#            self.assertTrue(len(data) == 1)
#            self.assertTrue('name' in data[0] and data[0]['name'] == 'USER1')

    def test_oneuser(self):
        with self.client:
            url = flask.url_for('users.info', _id=str(self.user.id()))
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])
            data = http.get(url)
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data)
            self.assertEqual(data['name'], 'USER1')
            self.assertFalse(project.model.PASSWORD_FIELDNAME in data)
            self.assertFalse('token' in data)


if __name__ == '__main__':
    unittest.main()
