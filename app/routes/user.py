import os
from app import app, bcrypt, db
from app.models import User
from app.validators import register_schema, login_schema
from app.response import Response
from flask import request, Blueprint, json
from flask_expects_json import expects_json
from flask_login import login_user, logout_user, login_required, current_user
from jsonschema import ValidationError
import smtplib

user = Blueprint("user", __name__)


@user.before_request
def log_request_info():
    if os.getenv("FLASK_ENV") != "production":
        app.logger.info(f"{request.path}")


"""
    Get data about user account
"""


@user.route("/whoami", methods=["GET"])
@login_required
def whoami():
    if hasattr(current_user, "username"):
        return Response(
            "Success",
            f"ID: {current_user.id}, Name: {current_user.name}, Surname: {current_user.surname}, Username: {current_user.username}",
            200,
        ).get()
    return Response("Failed", "You are not logged in", 400).get()


"""
    Login route
"""


@user.route("/login", methods=["POST"])
@expects_json(login_schema)
def login():

    data = request.get_json()

    user = User.query.filter_by(email=data["email"]).first()
    if user and bcrypt.check_password_hash(user.password, data["password"]):
        login_user(user)
        return Response(
            "Success", f"Successfully logged in as user: {user.username}", 200
        ).get()

    return Response("Failed", "Bad credentials, try again!", 400).get()


"""
    Register route
"""


@user.route("/register", methods=["POST"])
@expects_json(register_schema)
def register():

    data = request.get_json()

    if data["password"] != data["repeated_password"]:
        return Response("Failed", "Passwords do not match", 400).get()

    if User.query.filter_by(email=data["email"]).first():
        return Response(
            "Failed", "Account already exist with given email, try login instead!", 400
        ).get()

    if User.query.filter_by(username=data["username"]).first():
        return Response(
            "Failed", "Given username is taken, choose another one instead!", 400
        ).get()

    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    user = User(
        data["name"], data["surname"], data["email"], data["username"], hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return Response("Success", "Successfully registered!", 201).get()


"""
    Logout route
"""


@user.route("/logout", methods=["GET"])
@login_required
def logout():

    if hasattr(current_user, "username"):
        username = current_user.username
        logout_user()
        return Response(
            "Success", f"Successfully logged out user: {username}!", 200
        ).get()

    return Response("Failed", "You need to be logged in first", 400).get()


"""
    List all user
"""
# TODO List all users
@user.route("/users", methods=["GET"])
@login_required
def users():
    if hasattr(current_user, "user_type"):
        if current_user.user_type != "ADMIN":
            return Response("Failed", "Invalid permissions", 401).get()

        page = int(request.args.get("page")) if request.args.get("page") else 1
        perPage = (
            int(request.args.get("perPage")) if request.args.get("perPage") else 10
        )

        users = User.query.filter().offset((page - 1) * perPage).limit(perPage).all()

        resp = {"status": "Success", "payload": [usr.serialize() for usr in users]}
        response = app.response_class(
            response=json.dumps(resp), status=200, mimetype="Application/json"
        )
        return response


@user.errorhandler(400)
def bad_request(error):

    if isinstance(error.description, ValidationError):
        original_error = error.description
        return Response(
            "Failed", f"Validation error occurred: {original_error.message}", 400
        ).get()

    return error
