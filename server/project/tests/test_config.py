import unittest

from flask import Flask, current_app
from flask_testing import TestCase


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config.from_object('project.server.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(current_app.config['DEBUG'] is True)
        self.assertFalse(current_app is None)


class TestTestingConfig(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config.from_object('project.server.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['DATA_DIR'].endswith('-test'))
        self.assertTrue(current_app.config['DEBUG'])


class TestProductionConfig(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config.from_object('project.server.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertFalse(current_app.config['SECRET_KEY'] is 'my_precious')
        self.assertTrue(current_app.config['DEBUG'] is False)


if __name__ == '__main__':
    unittest.main()
