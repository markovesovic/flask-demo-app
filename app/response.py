from app import app
from flask import json


class Response:
    def __init__(self, status, message, statusCode) -> None:
        self.status = status
        self.message = message
        self.statusCode = statusCode

    def get(self):
        resp = {"status": self.status, "message": self.message}
        response = app.response_class(
            response=json.dumps(resp),
            status=self.statusCode,
            mimetype="Application/json",
        )
        return response
