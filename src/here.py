import binascii
import functools
import hashlib
import hmac
import json
import time
from base64 import b64encode
from urllib.parse import quote
from uuid import uuid4

import requests


class InvalidCredentialsError(RuntimeError):
    pass


class ExpiredAuthenticationError(RuntimeError):
    pass


def refresh_token(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except ExpiredAuthenticationError:
            self._refresh_token()
            return method(self, *args, **kwargs)

    return wrapper


class Client:
    _grant_type = "client_credentials"
    _oauth_signature_method = "HMAC-SHA256"
    _oauth_version = "1.0"
    _oauth_url = "https://account.api.here.com/oauth2/token"

    def __init__(self, oauth_consumer_key, access_key_secret):
        self._oauth_consumer_key = oauth_consumer_key
        self._access_key_secret = access_key_secret
        self._refresh_token()

    @refresh_token
    def optimal_tour(self, locations, times):
        with open("tmp/example.json") as fin:
            data = json.load(fin)
        requests.post(
            "https://tourplanning.hereapi.com/v2/problems",
            headers={"Authorization": f"Bearer {self._token}"},
            json=data,
        )

    def _refresh_token(self) -> str:
        oauth_nonce = str(uuid4())
        oauth_timestamp = str(int(time.time()))
        parameter_string = self._create_parameter_string(oauth_nonce, oauth_timestamp)
        encoded_base_string = (
            "POST&"
            + quote(self._oauth_url, safe="")
            + "&"
            + quote(parameter_string, safe="")
        )

        signing_key = self._access_key_secret + "&"
        oauth_signature = self._create_signature(signing_key, encoded_base_string)
        encoded_oauth_signature = quote(oauth_signature, safe="")

        data = {"grant_type": self._grant_type}
        headers = {
            "Authorization": (
                "OAuth"
                + f' oauth_consumer_key="{self._oauth_consumer_key}"'
                + f',oauth_nonce="{oauth_nonce}"'
                + f',oauth_signature="{encoded_oauth_signature}"'
                + f',oauth_signature_method="{self._oauth_signature_method}"'
                + f',oauth_timestamp="{oauth_timestamp}"'
                + f',oauth_version="{self._oauth_version}"'
            )
        }

        response = requests.post(self._oauth_url, data=data, headers=headers)
        if response.status_code != requests.codes.ok:
            raise InvalidCredentialsError(response.text)
        self._token = response.json()["access_token"]

    def _create_parameter_string(self, oauth_nonce, oauth_timestamp):
        return (
            f"grant_type={self._grant_type}"
            + f"&oauth_consumer_key={self._oauth_consumer_key}"
            + f"&oauth_nonce={oauth_nonce}"
            + f"&oauth_signature_method={self._oauth_signature_method}"
            + f"&oauth_timestamp={oauth_timestamp}"
            + f"&oauth_version={self._oauth_version}"
        )

    def _create_signature(self, secret_key, signature_base_string):
        encoded_string = signature_base_string.encode()
        encoded_key = secret_key.encode()
        hashed = hmac.new(encoded_key, encoded_string, hashlib.sha256).hexdigest()
        byte_array = b64encode(binascii.unhexlify(hashed))
        return byte_array.decode()
