from app import app
import os
from dotenv import load_dotenv


def main():
    load_dotenv()
    app.run(debug=os.getenv("DEBUG"))


if __name__ == "__main__":
    main()
