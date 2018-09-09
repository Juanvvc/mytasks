#!/usr/bin/env python3

import controller
from flask_cors import CORS

if __name__ == '__main__':
    CORS(controller.app)
    controller.app.run(debug=True)
