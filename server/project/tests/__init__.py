import json


def auth_header(username, password):
    import base64
    authstr = base64.b64encode('{}:{}'.format(username, password).encode()).decode()
    return 'Basic {}'.format(authstr)


class HTTPHelper(object):
    def __init__(self, client, auth):
        self.client = client
        self.auth = auth

    def get(self, url, auth=None):
        if auth is None:
            auth = self.auth
        response = self.client.get(url, headers={'Authorization': auth_header(auth[0], auth[1])})
        response_data = json.loads(response.data.decode())
        return response_data

    def post(self, url, data=None, auth=None):
        if auth is None:
            auth = self.auth
        if data is not None:
            response = self.client.post(url, data=json.dumps(data), content_type='application/json', headers={'Authorization': auth_header(auth[0], auth[1])})
        else:
            response = self.client.post(url, headers={'Authorization': auth_header(auth[0], auth[1])})
        response_data = json.loads(response.data.decode())
        return response_data

    def put(self, url, data=None, auth=None):
        if auth is None:
            auth = self.auth
        if data is not None:
            response = self.client.put(url, data=json.dumps(data), content_type='application/json', headers={'Authorization': auth_header(auth[0], auth[1])})
        else:
            response = self.client.put(url, headers={'Authorization': auth_header(auth[0], auth[1])})
        response_data = json.loads(response.data.decode())
        return response_data

    def delete(self, url, auth=None):
        if auth is None:
            auth = self.auth
        response = self.client.delete(url, headers={'Authorization': auth_header(auth[0], auth[1])})
        response_data = json.loads(response.data.decode())
        return response_data
