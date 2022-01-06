import os
from app import app, bcrypt, db
from app.models import User
from app.validators import register_schema, login_schema
from app.response import Response
from flask import request
from flask_expects_json import expects_json
from flask_login import login_user, logout_user, login_required, current_user
from jsonschema import ValidationError
import smtplib


@app.before_request
def log_request_info():
    if os.getenv("FLASK_ENV") != "production":
        app.logger.info(f"{request.path}")


"""
    Get data about user account
"""


@app.route("/whoami", methods=["GET"])
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


@app.route("/login", methods=["POST"])
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


@app.route("/register", methods=["POST"])
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


@app.route("/logout", methods=["GET"])
@login_required
def logout():

    if hasattr(current_user, "username"):
        username = current_user.username
        logout_user()
        return Response(
            "Success", f"Successfully logged out user: {username}!", 200
        ).get()

    return Response("Failed", "You need to be logged in first", 400).get()


@app.errorhandler(400)
def bad_request(error):

    if isinstance(error.description, ValidationError):
        original_error = error.description
        return Response(
            "Failed", f"Validation error occurred: {original_error.message}", 400
        ).get()

    return error
