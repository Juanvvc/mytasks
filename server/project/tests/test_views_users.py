import unittest
import flask_testing
import json
import project.model as model
from project.server import app


def auth_header(userid, password):
    import base64
    authstr = base64.b64encode('{}:{}'.format(userid, password).encode()).decode()
    return 'Basic {}'.format(authstr)


class TestUsersView(flask_testing.TestCase):
    def create_app(self):
        return app

    def setUp(self):
        user = model.create_user('USER1', 'PASSWORD1')
        user.create_group({'name': 'GROUP1'})

    def tearDown(self):
        import shutil
        shutil.rmtree(model.DATA_DIR)

    def test_availableusers(self):
        with self.client:
            response = self.client.get('/', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertTrue(type(data) == list)
            self.assertTrue(len(data) == 1)
            self.assertEqual(data[0]['name'], 'USER1')

    def test_oneuser(self):
        with self.client:
            response = self.client.get('/0', headers={'Authorization': auth_header(0, 'PASSWORD1')})
            data = json.loads(response.data.decode())
            self.assertEqual(data['name'], 'USER1')


if __name__ == '__main__':
    unittest.main()
