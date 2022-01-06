from flask import json
from flask.json import jsonify
from app import app
from app import db
from app.response import Response
from app.models import User, Arrangement
from flask import request
from flask_login import current_user


@app.route("/whoami", methods=["POST"])
def update():

    if hasattr(current_user, "username"):

        data = request.get_json()

        if data.get("email"):
            current_user.email = data["email"]
            db.session.add(current_user)
            db.session.commit()

            return Response("Success", "Email changed", 200).get()

    return Response("Failed", "You are not logged in", 400).get()


@app.route("/arrangements", methods=["GET"])
def get_arrangements():

    page = int(request.args.get("page")) if request.args.get("page") else 1
    perPage = int(request.args.get("perPage")) if request.args.get("perPage") else 10
    destination = request.args.get("destination")
    sort = request.args.get("sort")

    arrangements = (
        Arrangement.query.order_by(Arrangement.price)
        .filter_by(destination=destination)
        .offset((page - 1) * perPage)
        .limit(perPage)
        .all()
    )

    # print(f"{arrangements=}")

    print("Arrangements type")
    print(type(arrangements[0]))

    resp = {"status": "Success", "payload": [arr.serialize() for arr in arrangements]}
    response = app.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype="Application/json",
    )
    return response
