import os
import flask
from flask_cors import CORS


app = flask.Flask(__name__)
CORS(app)

app_settings = os.getenv(
    'APP_SETTINGS',
    'project.server.config.DevelopmentConfig'
)
app.config.from_object(app_settings)


@app.errorhandler(404)
@app.errorhandler(401)
def error_handler(error):
    return flask.make_response(flask.jsonify({'error_message': str(error), 'status': error.code}))
