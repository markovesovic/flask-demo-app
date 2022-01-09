from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import Arrangement, User, role_changes


def main():
    app = create_app()
    # app.run()
    with app.app_context():

        # db.create_all()

        for i in range(10):
            arrangement = Arrangement(
                datetime.now(),
                datetime.now(),
                "Belgrade",
                "Something nice",
                (i + 1) * 100,
                i + 10,
                "7f64a4ca-8d0b-4f46-ae3e-4974c4d21d3b",
            )
            db.session.add(arrangement)
        db.session.commit()


if __name__ == "__main__":
    main()
