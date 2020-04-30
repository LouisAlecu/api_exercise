from flask import request
import json
from .db_utils.schema import *


class Authenticator:
    """
    Just a decorator for authentication.
    """

    def __init__(self):
        self._reset_attributes()

    def _reset_attributes(self):
        self._credentials = {}
        self._user_id = {}

    def _get_user_id(self):
        """
        For the purpose of this exercise the expected input is {'user_id': <Int>}
        """
        self._user_id = request.headers.get("user_id")
        try:
            self._user_id = int(self._user_id)
        except:
            self._user_id = None
        print(self._user_id)

    def _validate_user_id(self):
        """
        Simulate some logic that would check the user data from our db against the user_id 
        sent in the headers as a parameter.
        """
        if self._user_id and type(self._user_id) == int:
            db_user_data = db.session.query(User).filter(User.id == self._user_id).all()
            self._credentials = {
                "user_id": db_user_data[0].id,
                "first_name": db_user_data[0].first_name,
                "last_name": db_user_data[0].last_name,
                "user_type": db_user_data[0].user_type,
            }
        elif self._user_id and not type(self._user_id) == int:
            self._credentials = {400: "user_id must be an int."}
        else:
            self._credentials = {
                "user_type": None,
                400: "need to pass a value user_id as an int in the headers.",
            }

    def login_user(self, called_function):
        def inner_function(*args, **kwargs):
            self._reset_attributes()
            self._get_user_id()
            self._validate_user_id()

            # This is where we call the funciton that has been decorated
            return_data = called_function(*args, **kwargs)
            # This is where we add the credentials to the response
            return_data_json = return_data.get_json()
            return_data_json["user_credentials"] = self._credentials
            return_data.set_data(
                json.dumps(return_data_json, indent=2, separators=(",", ": "))
            )
            return return_data

        return inner_function

    def get_user_credentials(self):
        # Now we have access to this method in the views
        """
        Just call this function in the views to get the user credentials.
        """
        return self._credentials
