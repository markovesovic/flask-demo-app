import smtplib
import os
from datetime import date, datetime
from app import db
from app.models import UserType, Arrangement
from app.util.validators import create_arrangement_schema
from app.util.response import Response
from flask import Blueprint, request
from flask_login import current_user
from flask_expects_json import expects_json
from flask_login.utils import login_required
from sqlalchemy.sql import text

admin = Blueprint("admin", __name__)


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


@admin.route("/arrangements", methods=["DELETE"])
@login_required
def delete_arrangement():

    if current_user.user_type == UserType.ADMIN:
        return Response("Failed", "Invalid permissions", 401).get()

    if not request.args.get("id"):
        return Response("Failed", "Please provide arrangement id", 400).get()

    arr = Arrangement.query.filter_by(id=request.args["id"]).first()

    if not arr:
        return Response("Failed", "There is no arrangement with given id", 400).get()

    # if (arr.start_date - datetime.now()).days < 5:
    #     return Response(
    #         "Failed",
    #         "There is less than 5 days till arrangement start. Deletion cannot be done!",
    #         400,
    #     ).get()

    # This line deletes arrangement
    # Arrangement.query.filter_by(id=id).delete()

    statement = text(
        f"""
        SELECT * FROM reservations 
        JOIN users u 
        ON reservations.user_id = u.id 
        WHERE reservations.arrangement_id = '{arr.id}';
        """
    )
    users = db.session.execute(statement)


    for row in users:

        message = f'Arrangement with {arr.id} has been canceled unfortunately!'

        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login(os.getenv('EMAIL'), os.getenv('EMAIL_PASSWORD'))
        # server.sendmail(os.getenv('EMAIL'), row[6], message)
        # server.close()


    return Response("Success", "Arrangement successfully deleted", 200).get()
