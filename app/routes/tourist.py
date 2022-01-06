from flask import json
from sqlalchemy.orm.session import Session
from app import app
from app import db
from app.response import Response
from app.models import User, Arrangement, reservations
from flask import request
from flask_login import current_user, login_required
from sqlalchemy.sql import text


"""
    Change user info
"""


@app.route("/whoami", methods=["POST"])
@login_required
def update():

    if hasattr(current_user, "username"):

        data = request.get_json()

        if data.get("email"):
            current_user.email = data["email"]
            db.session.add(current_user)
            db.session.commit()

            return Response("Success", "Email changed", 200).get()

    return Response("Failed", "You are not logged in", 400).get()


"""
    Get all arrangements with pagination and filtering
"""


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

    resp = {"status": "Success", "payload": [arr.serialize() for arr in arrangements]}
    response = app.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype="Application/json",
    )
    return response


"""
    Reserve arrangement by ID with some number of places
"""


@app.route("/reserve_arrangement", methods=["POST"])
@login_required
def reserve_arrangement():

    data = request.get_json()

    id = data.get("id")
    places = data.get("places")

    arrangement = Arrangement.query.filter_by(id=id).first()

    if not arrangement:
        return Response("Failed", "No arrangement with given id", 400).get()

    if arrangement.available_seats < places:
        return Response("Failed", "Not enough available places", 400).get()

    arrangement.available_seats -= places
    db.session.add(arrangement)
    ins = reservations.insert().values(
        user_id=current_user.id, arrangement_id=arrangement.id, places=places
    )
    db.session.execute(ins)
    db.session.commit()

    if places < 4:
        price = places * arrangement.price
    else:
        price = arrangement.price * (3 + (places - 3) * 0.9)

    return Response(
        "Success", f"Reservation was successfully made. Total price: {price}", 200
    ).get()


"""
    Get all arrangements by current user
"""


@app.route("/my_arrangements", methods=["GET"])
@login_required
def get_my_arrangements():

    page = int(request.args.get("page")) if request.args.get("page") else 1
    perPage = int(request.args.get("perPage")) if request.args.get("perPage") else 10

    statement = text(
        f"""SELECT * FROM reservations 
        JOIN arrangement a 
        ON a.id = reservations.arrangement_id 
        WHERE reservations.user_id = '{current_user.id}' 
        LIMIT {perPage} 
        OFFSET {(page - 1) * perPage}"""
    )
    my_arrangements = db.session.execute(statement)

    print(f"{my_arrangements=}")

    arrs = []
    for row in my_arrangements:
        arrs.append(
            {
                "your_seats": row[2],
                "id": row[3],
                "start_date": row[4],
                "end_date": row[5],
                "destination": row[6],
                "description": row[7],
                "price": row[8],
                "available_seats": row[9],
            }
        )

    resp = {
        "status": "Success",
        "payload": arrs,
    }
    response = app.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype="Application/json",
    )
    return response


"""
    Request new role
"""


@app.route("/request_new_role", methods=["POST"])
@login_required
def request_new_role():

    data = request.get_json()
    if data["role_type"]:

        if data["role_type"] != "admin" and data["role_type"] != "travel_guide":
            return Response("Failed", "Please provide valid role type", 400).get()

        message = f"User with username: {current_user.username} requested role: {data['role_type']}"

        #       ! Uncomment this line for sending mail
        """
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.getenv('EMAIL'), os.getenv('EMAIL_PASSWORD'))
        server.sendmail(os.getenv('EMAIL'), 'mare.vesovic@gmail.com', message)
        # server.sendmail(os.getenv('EMAIL'), current_user.email, message)
        server.close()
        """
        return Response("Success", "New role successfully requested", 200).get()

    return Response("Failed", "Please provide role_type field", 400).get()
