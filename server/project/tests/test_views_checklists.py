import unittest
import flask
import flask_testing
import project.model
import project.views
from project.tests import HTTPHelper


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
        self.user.create_child({'name': 'GROUP1'})
        self.group2 = self.user.create_child({'name': 'GROUP2', 'private': False})
        self.checklist1 = self.group2.create_child({'name': 'CHECKLIST1'})
        self.checklist2 = self.group2.create_child({'name': 'CHECKLIST2'})

        project.model.create_user('USER2', 'PASSWORD2')

    def tearDown(self):
        project.model.db.command('dropDatabase')

    def test_availablechecklists(self):
        with self.client:
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])
            url = flask.url_for('groups.info', _id=self.group2.id())
            data = http.get(url)
            checklists = data.get('checklists', [])
            self.assertTrue(type(checklists) == list)
            self.assertEqual(len(checklists), 2)
            self.assertTrue('name' in checklists[0] and checklists[0].get('name', '') in ('CHECKLIST1', 'CHECKLIST2'))

    def test_onechecklist(self):
        with self.client:
            url = flask.url_for('checklists.info', _id=self.checklist1.id())
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])
            data = http.get(url)
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'CHECKLIST1')

    def test_newchecklist(self):
        """ Test creation of checklist, and its errors """
        with self.client:
            url = flask.url_for('checklists.new')

            # try to create a checklist without information
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])
            data = http.post(url)
            self.assertEqual(data.get('status', 0), 400)

            # create a checklist
            new_info = dict(name='NEWNAME', _parentid=str(self.group2.id()))
            data = http.post(url, data=new_info)
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data)
            self.assertEqual(data['name'], 'NEWNAME')
            self.assertTrue('_parentid' in data)
            self.assertEqual(data['_parentid'], str(self.group2.id()))

    def test_updatechecklist(self):
        """ Test to update an item inside a checklist by updating the checklist: it should't be possible """
        with self.client:
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])

            # crate a new checklist with an item
            nc = self.group2.create_child({'name': 'NEWCHECKLIST'})
            nc.create_child({'name': 'NEWITEM'})

            # get information about the checklist
            url = flask.url_for('checklists.info', _id=str(nc.id()))
            data = http.get(url)
            # The new item must be in the checklist
            self.assertEqual(len(data['items']), 1)
            self.assertTrue(data['items'][0].get('name', None), 'NEWITEM')

            # get again the information in the checklist, and check the item has not changed
            data['items'][0]['name'] = 'ANOTHER NAME'
            data = http.post(url, data={'items': data['items']})
            self.assertFalse('error_message' in data)
            self.assertTrue(data['items'][0].get('name', None), 'NEWITEM')

    def test_updatechecklist2(self):
        """ Test to update a checklist, and its errors """
        with self.client:
            url = flask.url_for('checklists.info', _id=str(self.checklist1.id()))
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])

            # try to update a checklist without information
            data = http.put(url)
            self.assertTrue('error_message' in data)
            self.assertEqual(data['status'], 400)

            # update a checklist
            data = http.put(url, data=dict(name='NEWNAME2'))
            self.assertFalse('error_message' in data)
            self.assertTrue('name' in data and data['name'] == 'NEWNAME2')

            # USER2 can get but not update a checklist owned by USER1
            data = http.get(url, auth=["USER2", "PASSWORD2"])
            self.assertFalse('error_message' in data)
            data = http.put(url, data=dict(name='NEWNAME3'), auth=["USER2", "PASSWORD2"])
            self.assertTrue('error_message' in data)
            self.assertEqual(data['status'], 401)

    def test_deletechecklist(self):
        """ Test deleting a checklist, and its errors """
        with self.client:
            url = flask.url_for('checklists.info', _id=str(self.checklist1.id()))
            http = HTTPHelper(self.client, ['USER1', 'PASSWORD1'])

            # USER2 cannot delete a checklist owned by USER1
            data = http.get(url, auth=["USER2", "PASSWORD2"])
            self.assertFalse('error_message' in data)
            data = http.delete(url, auth=["USER2", "PASSWORD2"])
            self.assertEqual(data['status'], 401)
            data = http.get(url, auth=["USER2", "PASSWORD2"])
            self.assertFalse('error_message' in data)

            # USER1 can delete his own checklists
            data = http.delete(url)
            self.assertEqual(data.get('status', 0), 200)
            data = http.get(url)
            self.assertEqual(data.get('status', 0), 404)

            # non existing checklist
            url = flask.url_for('checklists.info', _id='XXX')
            data = http.delete(url)
            self.assertTrue('error_message' in data)
            self.assertEqual(data.get('status', 0), 404)


if __name__ == '__main__':
    unittest.main()
