from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from app import db
from app.models import Arrangement, User


def main():
    db.create_all()
    # users = User.query.all()
    # print(users)
    for i in range(10):
        arrangement = Arrangement(datetime.now(), datetime.now(), 'Belgrade', 'Something nice', (i+1)*100, i + 10)
        db.session.add(arrangement)
    db.session.commit()

if __name__ == "__main__":
    main()
