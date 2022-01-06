from dotenv import load_dotenv

load_dotenv()

from app import create_app
import os


def main():
    app = create_app()
    app.run(debug=os.getenv("DEBUG"))


if __name__ == "__main__":
    main()
