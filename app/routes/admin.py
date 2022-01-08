import smtplib
import os
from datetime import date, datetime
from app import app, db
from app.models import User, UserType, Arrangement, reservations
from app.util.validators import create_arrangement_schema, role_change_schema
from app.util.response import Response
from flask import Blueprint, request, json
from flask_login import current_user
from flask_expects_json import expects_json
from flask_login.utils import login_required
from sqlalchemy.sql import text

admin = Blueprint("admin", __name__)


"""
    View all arrangements
"""


@admin.route("/all_arrangements", methods=["GET"])
@login_required
def get_arrangements():

    if current_user.user_type == UserType.ADMIN:
        return Response("Failed", "Invalid permissions", 401).get()

    arrangements = Arrangement.query.order_by(Arrangement.price).all()

    resp = {"status": "Success", "payload": [arr.serialize() for arr in arrangements]}
    response = app.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype="Application/json",
    )
    return response


"""
    Creates new arrangement
"""


@admin.route("/arrangements", methods=["POST"])
@expects_json(create_arrangement_schema)
@login_required
def create_arrangement():

    if current_user.user_type == UserType.ADMIN:
        return Response("Failed", "Invalid permissions", 401).get()

    data = request.get_json()

    arrangement = Arrangement(
        data["start_date"],
        data["end_date"],
        data["destination"],
        data["description"],
        data["price"],
        data["available_seats"],
    )

    db.session.add(arrangement)
    db.session.commit()

    return Response("Success", "Arrangement successfully created", 201).get()


"""
    Updates arrangement with given id
"""


@admin.route("/arrangement/<id>", methods=["PUT"])
@login_required
def update_arrangement(id=None):

    if current_user.user_type == UserType.ADMIN:
        return Response("Failed", "Invalid permissions", 401).get()

    if not id:
        return Response("Failed", "No id provided", 400).get()

    arr = Arrangement.query.filter_by(id=id).first()

    if not arr:
        return Response("Failed", "There is no arrangement with given id", 400).get()

    # if (arr.start_date - datetime.now()).days < 5:
    #     return Response(
    #         "Failed",
    #         "There is less than 5 days till arrangement start. Update cannot be done!",
    #         400,
    #     ).get()

    data = request.get_json()

    if data.get("description"):
        arr.description = data["description"]
    if data.get("available_seats"):
        arr.available_seats = data["available_seats"]
    if data.get("destination"):
        arr.destination = data["destination"]
    if data.get("price"):
        arr.price = data["price"]

    db.session.add(arr)
    db.session.commit()

    return Response("Success", "Successfully updated arrangement", 200).get()


"""
    Deletes arrangement with given id and notifies all subscribed users
"""


@admin.route("/arrangement/<id>", methods=["DELETE"])
@login_required
def delete_arrangement(id=None):

    if current_user.user_type == UserType.ADMIN:
        return Response("Failed", "Invalid permissions", 401).get()

    if not id:
        return Response("Failed", "Please provide arrangement id", 400).get()

    arr = Arrangement.query.filter_by(id=id).first()

    if not arr:
        return Response("Failed", "There is no arrangement with given id", 400).get()

    # if (arr.start_date - datetime.now()).days < 5:
    #     return Response(
    #         "Failed",
    #         "There is less than 5 days till arrangement start. Deletion cannot be done!",
    #         400,
    #     ).get()

    # This line deletes arrangement
    Arrangement.query.filter_by(id=id).delete()
    db.session.commit()

    # This gets all users that subscibed to given arrangement
    statement = text(
        f"""
        SELECT * FROM reservations 
        JOIN users u 
        ON reservations.user_id = u.id 
        WHERE reservations.arrangement_id = '{arr.id}';
        """
    )
    users = db.session.execute(statement)
    db.session.commit()

    # Sending mails
    for row in users:

        message = f"Arrangement with {arr.id} has been canceled unfortunately!"

        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login(os.getenv('EMAIL'), os.getenv('EMAIL_PASSWORD'))
        # server.sendmail(os.getenv('EMAIL'), row[6], message)
        # server.close()

    # This deletes all reservations
    statement = text(
        f"""
        DELETE FROM reservations
        WHERE arrangement_id = '{id}'
        """
    )
    db.session.execute(statement)
    db.session.commit()

    return Response("Success", "Arrangement successfully deleted", 200).get()


@admin.route("/role_changes", methods=["GET"])
@login_required
def role_changes():

    if current_user.user_type == UserType.ADMIN:
        return Response("Failed", "Invalid permissions", 401).get()

    statement = text("SELECT * FROM role_changes")
    rows = db.session.execute(statement)

    items = []
    for row in rows:
        items.append({"user_id": row[0], "requested_role": row[1]})

    resp = {
        "status": "Success",
        "payload": items,
    }
    response = app.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype="Application/json",
    )
    return response


@admin.route("/role_change/<id>", methods=["POST"])
@expects_json(role_change_schema)
@login_required
def role_change(id=None):

    if current_user.user_type == UserType.ADMIN:
        return Response("Failed", "Invalid permissions", 401).get()

    if not id:
        return Response("Failed", "Please provide id", 400).get()

    data = request.get_json()

    # Send mail with status and message!

    statement = text(
        f"""SELECT requested_role FROM role_changes WHERE user_id = '{id}'"""
    )
    role = db.session.execute(statement).first()[0]
    print(f'{role=}')

    statement = text(
        f"""DELETE FROM role_changes WHERE user_id = '{id}'"""
    )
    db.session.execute(statement)
    db.session.commit()

    # Actually change role
    if data["action"] == "approved":

        user = User.query.filter_by(id=id).first()
        user.user_type = role
        db.session.add(user)
        db.session.commit()

        return Response("Success", "User role successfully changed", 201).get()

    return Response("Success", "User role change denied", 200).get()