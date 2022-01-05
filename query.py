from app import db
from dotenv import load_dotenv
from app.models import User


def main():
    load_dotenv()
    # db.create_all()
    users = User.query.all()
    print(users)


if __name__ == "__main__":
    main()
