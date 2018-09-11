#!/usr/bin/env python3
import os
import unittest
import coverage
import logging
from flask_script import Manager

import project.server
import project.views

logger = logging

COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/tests/*',
        'project/server/config.py'
    ]
)
COV.start()

manager = Manager(project.server.app)


@manager.command
def test():
    """Runs the unit tests without test coverage."""
    project.server.configure_app('project.server.config.TestingConfig')
    project.views.register(project.server.app)

    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def cov():
    """Runs the unit tests with coverage."""
    project.server.configure_app('project.server.config.TestingConfig')
    project.views.register(project.server.app)

    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report(show_missing=True)
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
        return 0
    return 1


@manager.command
def list_routes():
    project.views.register(project.server.app)

    import urllib.parse
    output = []
    for rule in project.server.app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)

    for line in sorted(output):
        print(line)


@manager.command
def devel():
    project.server.configure_app('project.server.config.DevelopmentConfig')
    project.views.register(project.server.app)
    project.server.app.run(debug=True)


@manager.command
def passwd(userid, password):
    project.server.configure_app('project.server.config.DevelopmentConfig')
    import project.model as model
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
    project.server.configure_app('project.server.config.ProductionConfig')
    project.views.register(project.server.app)
    project.server.app.run(debug=True)


if __name__ == '__main__':
    manager.run()
