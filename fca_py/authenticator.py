from flask import request
import json


class Authenticator:
    def __init__(self):
        self._reset_attributes()

    def _reset_attributes(self):
        self._credentials = {}
        self._token = {}

    def _get_token(self):
        # Here we pretend we get a token. The actual input that is expected for
        # The purpose of this exercise is {'token': {'user_type': <user|staff>}}
        self._token = request.headers.get("user_type")
        print(self._token)

    def _validate_token(self):
        # Here we try to simulate, in a very simplified way, some JWT logic that would determine the user type
        # based on what we found in the request headers. Also for the aforementioned purpose I`ve written the code below
        # in a verbose way.
        # For simplicity, we assume that it is a user or a staff if the headers say so.
        if self._token == "user":
            self._credentials["user_type"] = "user"
        elif self._token == "staff":
            self._credentials["user_type"] = "staff"
        else:
            self._credentials["user_type"] = "Not authenticated"

    def login_user(self, called_function):
        def inner_function(*args, **kwargs):
            self._reset_attributes()
            self._get_token()
            self._validate_token()

            # This is where we call the funciton that has been decorated
            return_data = called_function(*args, **kwargs)
            # This is where we add the credentials
            return_data_json = return_data.get_json()
            return_data_json["user_credentials"] = self._credentials
            return_data.set_data(
                json.dumps(return_data_json, indent=2, separators=(",", ": "))
            )
            return return_data

        return inner_function

    def get_user_credentials(self):
        # Now we have access to this method in the views
        return self._credentials
