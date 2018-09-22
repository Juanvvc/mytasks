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

### Additional management commands in the server

- `./mytasks.sh test`: run tests on the server
- `./mytasks.sh cov`: run tests on the server with coverage
- `./mytasks.sh passwd USER PASSWORD`: change a password for a user
- `./mytasks.sh list_routes`: list available routes

## Client

Run yarn:

```
cd client
yarn
yarn serve
```

Background: https://wallpapercave.com/w/4MQzQAg
