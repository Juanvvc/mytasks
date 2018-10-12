# Installation

A task manager system for the web. Server and client.

## Server

Mytasks use pipenv to manage dependencies. To install pipenv:

```
sudo apt-get install python3-pipenv
pip3 install --user pipenv
```

The first time you run the server, dependencies are installed with pypenv.

```
cd server
./mytasks.sh
```

### Configuration

Create a file named `server/config.py`. This file is local, it might include
usernames, secrets and passwords and SHOULDN'T be added to git. Example:

```
import project.server.config

class MytasksConfig(project.server.config.DevelopmentConfig):
    MONGOURL = 'mongodb://USER:PASSWORD@localhost:27017/?authSource=admin'
    # generate with: python3 -c 'import os; print(os.urandom(32))'
    SECRET_KEY = b'?\xbf,\xb4\x8d\xa3"<\x9c\xb0@\x0f5\xab,w\xee\x8d$0\x13\x8b83'
```

### Unittesting the application

Unit tests must use a testing database. You can run a MongoDB server without
autentication on an empty directory:

```
mkdir -p dbtest
mongod --dbpath dbtest
rm -rf dbtest

cd server
./mytasks.sh test
```

### Additional management commands in the server

- `./mytasks.sh test`: run tests on the server
- `./mytasks.sh cov`: run tests on the server with coverage
- `./mytasks.sh passwd USER PASSWORD`: change a password for a user
- `./mytasks.sh routes`: list available routes

## Client

Run yarn:

```
cd client
yarn
yarn serve
```

### Configuration

Create a file named `client/public/local/local.js` and  `client/public/local/local.css`.
These files are local and SHOULDN'T be added to git. Example:

```
/* local.js */
window.MYTASKS_SERVER='https://myserver.com/mytasks/api';
```

```
/* local.css */
.application--wrap {
  /* Set the background here and not in App.vue to prevent attaching the background to the application */
  background-color: #ccccde;
  background-image: url("wallpaper.jpg");
  background-size: auto;
  background-attachment: fixed;
}
```
