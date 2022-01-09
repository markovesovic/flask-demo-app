from datetime import datetime
from app import app, db
from app.util.response import Response
from app.util.validators import reserve_schema, request_new_role_schema
from app.models import User, Arrangement, UserType, reservations
from flask import request, Blueprint, json
from flask_expects_json import expects_json
from flask_login import current_user, login_required
from sqlalchemy.sql import text


tourist = Blueprint("tourist", __name__)


"""
    Get all arrangements with pagination and filtering
"""


@tourist.route("/arrangements", methods=["GET"])
def get_arrangements():

    page = int(request.args.get("page")) if request.args.get("page") else 1
    perPage = int(request.args.get("perPage")) if request.args.get("perPage") else 10
    destination = request.args.get("destination")
    sort = request.args.get("sort")

    arrangements = None

    if destination and sort:
        arrangements = (
            Arrangement.query.order_by(sort)
            .filter_by(destination=destination)
            .offset((page - 1) * perPage)
            .limit(perPage)
            .all()
        )
    elif destination:
        arrangements = (
            Arrangement.query.filter_by(destination=destination)
            .offset((page - 1) * perPage)
            .limit(perPage)
            .all()
        )
    elif sort:
        arrangements = (
            Arrangement.query.sort(sort)
            .offset((page - 1) * perPage)
            .limit(perPage)
            .all()
        )
    else:
        arrangements = (
            Arrangement.query.offset((page - 1) * perPage).limit(perPage).all()
        )

    resp = {
        "status": "Success",
        "page": page,
        "perPage": perPage,
        "payload": [arr.serialize() if current_user.is_authenticated else arr.serialize_short() for arr in arrangements],
    }
    response = app.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype="Application/json",
    )
    return response


"""
    Reserve arrangement by ID with some number of places
"""


@tourist.route("/reserve_arrangement", methods=["POST"])
@login_required
@expects_json(reserve_schema)
def reserve_arrangement():

    data = request.get_json()

    id = data.get("id")
    places = data.get("places")

    arrangement = Arrangement.query.filter_by(id=id).first()

    if not arrangement:
        return Response("Failed", "No arrangement with given id", 400).get()

    if (arrangement.start_date - datetime.now()).days < 5:
        return Response(
            "Failed",
            "There is less than 5 days till arrangement start. Reservation cannot be done!",
            400,
        ).get()

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
        "Success", f"Reservation was successfully made. Total price: {price}", 201
    ).get()


"""
    Get all arrangements by current user
"""


@tourist.route("/my_arrangements", methods=["GET"])
@login_required
def get_my_arrangements():

    page = int(request.args.get("page")) if request.args.get("page") else 1
    perPage = int(request.args.get("perPage")) if request.args.get("perPage") else 10

    statement = text(
        f"""SELECT * FROM reservations 
        JOIN arrangements a 
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


@tourist.route("/request_new_role", methods=["POST"])
@login_required
@expects_json(request_new_role_schema)
def request_new_role():

    data = request.get_json()
    if (
        data["role_type"] != UserType.ADMIN.name
        and data["role_type"] != UserType.TOUR_GUIDE.name
    ):
        return Response("Failed", "Please provide valid role type", 400).get()

    statement = text(
        f"""SELECT user_id FROM role_changes WHERE user_id = '{current_user.id}'"""
    )
    row = db.session.execute(statement)

    if row.first():
        return Response(
            "Failed", "There is already pending request for this user", 400
        ).get()

    role_type = (
        UserType.ADMIN.name
        if data["role_type"] == UserType.ADMIN
        else UserType.TOUR_GUIDE.name
    )

    statement = text(
        f"""
        INSERT INTO role_changes (user_id, requested_role)
        VALUES('{current_user.id}', '{role_type}')
        """
    )
    db.session.execute(statement)
    db.session.commit()

    message = f"User with username: {current_user.username} requested role: {data['role_type']}"

    #       ! Uncomment string bellow for sending mail
    """
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.getenv('EMAIL'), os.getenv('EMAIL_PASSWORD'))
    server.sendmail(os.getenv('EMAIL'), current_user.email, message)
    server.close()
    """

    return Response("Success", "New role successfully requested", 200).get()
