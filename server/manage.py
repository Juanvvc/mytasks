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


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(401)
@app.errorhandler(500)
def error_handler(error):
    return flask.make_response(flask.jsonify({'error_message': str(error), 'status': error.code}))


@app.cli.command()
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


@app.cli.command()
@click.argument('userid')
@click.argument('password')
def passwd(userid, password):
    app.config.from_object('project.server.config.DevelopmentConfig')
    project.model.configure_model(app)

    import project.model as model
    user = model.search_user(int(userid))
    if user is not None:
        user.hash_password(password)
        if not user.save():
            app.logger.warning('Cannot save password')
    else:
        app.logger.warning('User no found: %s', userid)


@app.cli.command()
@click.argument('username')
@click.argument('password')
def useradd(username, password):
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
