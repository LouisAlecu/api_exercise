import requests


class ApiClient:
    """
    Just a little class to help us get the amazon_ids. Obviously, it would need some
    more error handling, but it should do for the purpose of this exercise.
    """

    def __init__(self):
        self._root_endpoint = "http://openlibrary.org/api/books"
        self._response = None
        self._last_req_status = None

    def get_response(self, isbn):
        params = {"bibkeys": f"ISBN:{isbn}", "jscmd": "data", "format": "json"}
        self._response = requests.get(self._root_endpoint, params=params)
        self._last_req_status = self._response.status_code
        return self._response

    def get_request_status(self):
        return self._last_req_status

    def get_json(self):
        return self._data

    def get_response_object_itself(self):
        return self._response
