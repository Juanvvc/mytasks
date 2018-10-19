import unittest
import flask
import flask_testing
import project.model
import project.views
from project.tests import HTTPHelper


class TestItemsView(flask_testing.TestCase):
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
        self.user2 = project.model.create_user('USER2', 'PASSWORD2')
        self.group = self.user.create_child({'name': 'GROUP1', 'private': False})
        self.group2 = self.user.create_child({'name': 'GROUP1', 'private': True})
        self.checklist1 = self.group.create_child({'name': 'CHECKLIST1'})
        self.checklist2 = self.group2.create_child({'name': 'CHECKLIST2'})
        self.item1 = self.checklist1.create_child({'name': 'ITEM1'})
        self.item2 = self.checklist1.create_child({'name': 'ITEM2'})
        self.item3 = self.checklist2.create_child({'name': 'ITEM3'})

        project.model.create_user('USER2', 'PASSWORD2')

    def tearDown(self):
        project.model.db.command('dropDatabase')

    def test_availableitems(self):
        with self.client:
            url = flask.url_for('checklists.info', _id=str(self.checklist1.id()))
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])
            data = http.get(url)
            items = data.get('items', [])
            self.assertTrue(type(items) == list)
            self.assertEqual(len(items), 2)
            self.assertTrue(items[0].get('name', '') in ('ITEM1', 'ITEM2'))

    def test_oneitem(self):
        with self.client:
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])

            # USER1 can access item1
            url = flask.url_for('items.info', _id=str(self.item1.id()))
            data = http.get(url)
            self.assertFalse('error_message' in data)
            self.assertEqual(data.get('name', None), 'ITEM1')
            # USER2 can access to item1, since it is in a private group
            data = http.get(url, auth=['USER2', 'PASSWORD2'])
            self.assertFalse('error_message' in data)
            self.assertEqual(data.get('name', None), 'ITEM1')

            # USER1 can access item3
            url = flask.url_for('items.info', _id=str(self.item3.id()))
            data = http.get(url)
            self.assertFalse('error_message' in data)
            self.assertEqual(data.get('name', None), 'ITEM3')
            # USER2 cannot access to item3, since it is in a private group
            data = http.get(url, auth=['USER2', 'PASSWORD2'])
            self.assertEqual(data.get('name', None), None)
            self.assertTrue('error_message' in data)
            self.assertEqual(data.get('status', 0), 401)

    def test_newitem(self):
        """ Test creation of an item, and its errors """
        with self.client:
            url = flask.url_for('items.new')
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])

            # try to create an item without information
            data = http.post(url)
            self.assertEqual(data.get('status', 0), 400)

            # create an item
            new_info = dict(name='NEWNAME', parentid=str(self.checklist1.id()))
            data = http.post(url, data=new_info)
            self.assertFalse('error_message' in data)
            self.assertEqual(data.get('name', None), 'NEWNAME')
            self.assertEqual(data.get('parentid', None), str(self.checklist1.id()))

    def test_updateitem(self):
        """ Test to update an item, and its errors """
        with self.client:
            url = flask.url_for('items.info', _id=str(self.item3.id()))
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])

            # try to update an item without information
            data = http.put(url)
            self.assertTrue('error_message' in data)
            self.assertEqual(data['status'], 400)
            # get item3, check the old name
            data = http.get(url)
            self.assertEqual(data.get('name', None), 'ITEM3')
            # update item3
            data = http.post(url, data=dict(name='NEWNAME'))
            self.assertTrue('error_message' not in data)
            # get item3, check the new name
            data = http.get(url)
            self.assertEqual(data.get('name', None), 'NEWNAME')
            # get the information of the checklist, test the name is new one
            data = http.get(flask.url_for('checklists.info', _id=data['parentid']))
            self.assertEqual(data['items'][0].get('name', None), 'NEWNAME')

            # USER2 can get but not update an item in a public group owned by USER1
            url = flask.url_for('items.info', _id=str(self.item1.id()))
            data = http.get(url, auth=["USER2", "PASSWORD2"])
            self.assertFalse('error_message' in data)
            data = http.put(url, data=dict(name='NEWNAME1'), auth=["USER2", "PASSWORD2"])
            self.assertTrue('error_message' in data)
            self.assertEqual(data['status'], 401)

    def test_deleteitem(self):
        """ Test deleting an item, and its errors """
        with self.client:
            url = flask.url_for('items.info', _id=str(self.item3.id()))
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])

            # check USER2: he cannot delete the item
            data = http.delete(url, auth=['USER2', 'PASSWORD2'])
            self.assertEqual(data.get('status', 0), 401)

            # check item3 exists
            data = http.get(url)
            self.assertEqual(data.get('name', None), 'ITEM3')
            # delete item3
            data = http.delete(url)
            self.assertEqual(data.get('status', 0), 200)
            # check it does not exist
            data = http.get(url)
            self.assertEqual(data.get('status', 0), 404)
            data = http.delete(url)
            self.assertEqual(data.get('status', 0), 404)
            # check item3 also does not exist in the checklist
            url = flask.url_for('checklists.info', _id=str(self.checklist2.id()))
            data = http.get(url)
            self.assertEqual(len(data['items']), 0)

            # non existing checklist
            url = flask.url_for('checklists.info', _id='XXX')
            data = http.delete(url)
            self.assertTrue('error_message' in data)
            self.assertEqual(data.get('status', 0), 404)


if __name__ == '__main__':
    unittest.main()
