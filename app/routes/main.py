import os
from app import app
from app.response import Response
from jsonschema import ValidationError
from flask import Blueprint, request

main = Blueprint("main", __name__)


@main.errorhandler(400)
def bad_request(error):

    if isinstance(error.description, ValidationError):
        original_error = error.description
        return Response(
            "Failed", f"Validation error occurred: {original_error.message}", 400
        ).get()

    return error


@main.before_request
def log_request_info():
    if os.getenv("FLASK_ENV") != "production":
        app.logger.info(f"{request.path}")
