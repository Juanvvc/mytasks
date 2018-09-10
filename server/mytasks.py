#!/usr/bin/env python3
import os
import unittest
import coverage

from project.server import app

from flask_script import Manager

COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/tests/*',
        'project/server/config.py',
        'project/server/*/__init__.py'
    ]
)
COV.start()

manager = Manager(app)


@manager.command
def test():
    """Runs the unit tests without test coverage."""
    app.config.from_object('project.server.config.TestingConfig')
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
        return 0
    return 1


@manager.command
def devel():
    app.config.from_object('project.server.config.DevelopmentConfig')
    import project.server.controller
    app.run(debug=True)


@manager.command
def run():
    app.config.from_object('project.server.config.ProductionConfig')
    app.run(debug=False)


if __name__ == '__main__':
    manager.run()
