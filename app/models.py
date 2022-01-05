import uuid
from enum import Enum
from app import db, loginManager
from sqlalchemy.dialects.postgresql import UUID
from flask_login import UserMixin


@loginManager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class UserType(Enum):
    TOURIST = 1
    TOUR_GUIDE = 2
    ADMIN = 3


class User(db.Model, UserMixin):
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
