import uuid
from enum import Enum
from app import db, login_manager
from sqlalchemy.dialects.postgresql import UUID
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class UserType(Enum):
    TOURIST = 1
    TOUR_GUIDE = 2
    ADMIN = 3


reservations = db.Table(
    "reservations",
    db.Column("user_id", db.ForeignKey("users.id")),
    db.Column("arrangement_id", db.ForeignKey("arrangements.id")),
    db.Column("places", db.Integer, nullable=False),
)

role_changes = db.Table(
    "role_changes",
    db.Column("user_id", db.ForeignKey("users.id"), unique=True),
    db.Column("requested_role", db.Enum(UserType), nullable=False),
)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(20), unique=False, nullable=False)
    surname = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_type = db.Column(db.Enum(UserType), nullable=False, default=UserType.TOURIST)

    def __init__(self, name, surname, email, username, password):
        self.name = name
        self.surname = surname
        self.email = email
        self.username = username
        self.password = password

    def __repr__(self) -> str:
        return f"UUID: {self.id}, USERNAME: {self.username}, EMAIL: {self.email}, PASSWORD: {self.password}"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
            "username": self.username,
            "user_type": self.user_type.name,
        }


class Arrangement(db.Model):
    __tablename__ = "arrangements"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_date = db.Column(db.DateTime(timezone=False), unique=False, nullable=False)
    end_date = db.Column(db.DateTime(timezone=False), unique=False, nullable=False)
    destination = db.Column(db.String(30), unique=False, nullable=False)
    description = db.Column(db.Text(), unique=False, nullable=False)
    price = db.Column(db.Float, unique=False, nullable=False)
    available_seats = db.Column(db.Integer, unique=False, nullable=False)
    creator = db.Column(db.ForeignKey("users.id"), unique=False, nullable=False)
    tour_guide = db.Column(db.ForeignKey("users.id"), unique=False, nullable=True)

    def __init__(
        self,
        start_date,
        end_date,
        destination,
        description,
        price,
        available_seats,
        creator,
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.destination = destination
        self.description = description
        self.price = price
        self.available_seats = (available_seats,)
        self.creator = creator

    def __repr__(self) -> str:
        return f"{{Destination: {self.destination}, Price: {self.price}, Seats left: {self.available_seats}}}"

    def serialize(self):
        return {
            "id": self.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "destination": self.destination,
            "description": self.description,
            "price": self.price,
            "available_seats": self.available_seats,
        }

    def serialize_short(self):
        return {
            "destination": self.destination,
            "description": self.description,
        }
