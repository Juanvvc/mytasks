import os
import click
import unittest
from flask_cors import CORS
import flask
import project.views

app_settings = os.getenv(
    'APP_SETTINGS',
    'project.server.config.DevelopmentConfig'
)
app = flask.Flask(__name__)
app.config.from_object(app_settings)
CORS(app)

project.model.configure_model(app)
project.views.register(app)


@app.cli.command()
@click.argument('username')
@click.argument('password')
def passwd(username, password):
    " Change the password for a user "
    project.model.configure_model(app)

    import project.model as model
    user = model.search_username(username)
    if user is not None:
        user.hash_password(password)
        if not user.save():
            app.logger.warning('Cannot save password')
    else:
        app.logger.warning('User no found: %s', username)


@app.cli.command()
@click.argument('username')
@click.argument('password')
def useradd(username, password):
    " Add a user to the model "
    import project.model as model
    model.create_user(username, password)


@app.cli.command()
def test():
    """Runs the unit tests without test coverage."""
    app.config.from_object('project.server.config.TestingConfig')
    project.model.configure_model(app)

    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@app.cli.command()
def test_model():
    """Runs the unit tests, only for models"""
    app.config.from_object('project.server.config.TestingConfig')
    project.model.configure_model(app)

    tests = unittest.TestLoader().discover('project/tests', pattern='test_model*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@app.cli.command()
def test_views():
    """Runs the unit tests , only for views """
    app.config.from_object('project.server.config.TestingConfig')
    project.model.configure_model(app)

    tests = unittest.TestLoader().discover('project/tests', pattern='test_views*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@app.cli.command()
def cov():
    """Runs the unit tests with coverage."""
    import coverage
    COV = coverage.coverage(
        branch=True,
        include='project/*',
        omit=[
            'project/tests/*',
            'project/server/config.py'
        ]
    )
    COV.start()

    app.config.from_object('project.server.config.TestingConfig')
    project.model.configure_model(app)

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
