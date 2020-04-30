import requests


class ApiClient:
    def __init__(self):
        self._root_endpoint = "http://openlibrary.org/api/books"
        self._response = None
        self._last_req_status = None

    def get_response(self, isbn):
        params = {"bibkeys": f"ISBN:{isbn}", "jscmd": "data", "format": "json"}
        self._response = requests.get(self._root_endpoint, params=params)
        self._last_req_status = self._response.status_code
        return self._response

    def _error_handling(self):
        if self._last_req_status == 200:
            print("Request executed successfully.")
            return True
        elif self._last_req_status == 403:
            print("You exceeded the requests limit.")
        elif self._last_req_status == 401:
            print("Unauthorized access. Probably invalid credentials.")
        elif self._last_req_status == 400:
            print("Bad request.")
        else:
            print("The response code is {self._last_req_status}")
        return False

    def get_request_status(self):
        return self._last_req_status

    def get_json(self):
        return self._data

    def get_response_object_itself(self):
        return self._response
