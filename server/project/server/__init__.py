import flask
import logging
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import Bcrypt

app = flask.Flask(__name__)
CORS(app)

app.config.from_object('project.server.config.BaseConfig')

auth = HTTPBasicAuth()
logger = logging.getLogger(__name__)

bcrypt = Bcrypt(app)
