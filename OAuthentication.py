from requests_oauthlib import OAuth1Session
from flask import session
from oauthlib.oauth1 import Client

class OAuthentication:

    def __init__(self):
        self.client_key = 'https://www.creditagricolestore.fr/castore-oauth/resources/1/oauth/consumer/b81bbad2a8d847bdbbd5952ad92f06c3'
        self.client_secret = '4fcdd7b6ed34433ca8302af88289a89f'
        self.request_token_url = 'https://www.creditagricolestore.fr/castore-oauth/resources/1/oauth/get_request_token'
        self.authorization_url = 'https://www.creditagricolestore.fr/castore-data-provider/authentification'
        self.callback_uri = 'http://localhost:5000/callback'
        self.verifier = None
        self.access_token_url = 'https://www.creditagricolestore.fr/castore-oauth/resources/1/oauth/get_access_token'

    def getRequestToken(self):
        self.oauth_session = OAuth1Session(self.client_key, client_secret=self.client_secret, signature_type='auth_header', callback_uri=self.callback_uri, client_class=CustomClient)
        request_token = self.oauth_session.fetch_request_token(self.request_token_url)
        self.oauth_token = request_token['oauth_token']
        self.oauth_token_secret = request_token['oauth_token_secret']

    def getAccessToken(self):
        self.credentials = self.oauth_session.fetch_access_token(self.access_token_url, verifier=self.verifier)
        print(type(self.credentials))



class CustomClient(Client):
    def _render(self, request, formencode=False, realm=None):
        request.headers['Accept'] = "application/json, application/x-www-form-urlencoded"
        return super(CustomClient, self)._render(request, formencode, realm)