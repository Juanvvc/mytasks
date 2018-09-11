import flask
from flask_cors import CORS
import project.model
import project.views

app = flask.Flask(__name__)
CORS(app)


def configure_app(app_settings):
    app.config.from_object(app_settings)

    # configure the model.
    project.model.DATA_DIR = app.config.get('DATA_DIR')


@app.errorhandler(404)
@app.errorhandler(401)
def error_handler(error):
    return flask.make_response(flask.jsonify({'error_message': str(error), 'status': error.code}))
