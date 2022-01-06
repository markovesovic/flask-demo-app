from dotenv import load_dotenv

load_dotenv()

from app import app
import os


def main():
    app.run(debug=os.getenv("DEBUG"))


if __name__ == "__main__":
    main()
