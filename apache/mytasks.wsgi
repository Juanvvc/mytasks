# Apache2 configuration example:
#
# WSGIDaemonProcess localhost processes=2 threads=15 display-name=%{GROUP}
# WSGIProcessGroup localhost
# WSGIScriptAlias /hello /path/to/mytasks/root/mytasks.wsgi
# WSGIScriptReloading On
# <Directory /path/to/mytasks/root/apache>
# <IfVersion < 2.4>
#   Order allow,deny
#   Allow from all
# </IfVersion>
# <IfVersion >= 2.4>
#   Require all granted
# </IfVersion>
# </Directory>

import os.path
server_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'server')

# activate environment
activate_this = os.path.join(server_dir, '.venv', 'bin', 'activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# add server dir to the sys path
import sys
sys.path.insert(0, server_dir)

# import application
from manage import app as application
