from app import app, db
from flask import Blueprint, request, json
from flask_login import login_required, current_user
from app.models import Arrangement, UserType
from app.util.response import Response

tour_guide = Blueprint("tour_guide", __name__)


@tour_guide.before_request
@login_required
def log_request_info():
    if current_user.user_type != UserType.TOUR_GUIDE:
        return Response("Failed", "Invalid permissions", 403).get()


@tour_guide.route("/my_arrangements", methods=["GET"])
@login_required
def my_arrangements():

    arrangements = Arrangement.query.filter_by(tour_guide=current_user.id).all()

    resp = {"status": "Success", "payload": [arr.serialize() for arr in arrangements]}

    response = app.response_class(
        response=json.dumps(resp), status=200, mimetype="Application/json"
    )
    return response


@tour_guide.route("/arrangement/<id>/description", methods=["PUT"])
@login_required
def change_description(id=None):

    if not id:
        return Response("Failed", "No id provided", 400).get()

    data = request.get_json()

    if not data.get("new_description"):
        return Response("Failed", "Pls provide new_description", 400).get()

    arr = Arrangement.query.filter_by(id=id).first()

    if arr.tour_guide != current_user.id:
        return Response("Failed", "No permission to change description", 400).get()

    if (arr.end_date - arr.start_date).days < 5:
        return Response(
            "Failed",
            "Cannot change description because arrangement starts within 5 days",
            400,
        ).get()

    arr.description = data["new_description"]
    db.session.add(arr)
    db.session.commit()

    return Response("Success", "Description updated", 201).get()
