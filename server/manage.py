#!/usr/bin/env python3
import os
import unittest
import coverage
import logging
from flask_script import Manager

from project.server import app

logger = logging

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
    app.config.from_object('project.server.config.TestingConfig')
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
    import project.views
    import project.server.auth

    auth = project.server.auth.get_auth(app)
    for blueprint in project.views.get_blueprints(app, auth):
        app.register_blueprint(blueprint)

    app.run(debug=True)


@manager.command
def passwd(userid, password):
    import project.server.model as model
    user = model.search_user(int(userid))
    if user is not None:
        user.hash_password(password)
        if not user.save():
            logger.warning('Cannot save password')
    else:
        logger.warning('User no found: %s', userid)


@manager.command
def useradd(username, password):
    import project.server.model as model
    model.create_user(username, password)


@manager.command
def run():
    app.config.from_object('project.server.config.ProductionConfig')
    app.run(debug=False)


if __name__ == '__main__':
    manager.run()
