from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config


app = Flask(__name__)

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from app.routes.user import user
    from app.routes.tourist import tourist
    from app.routes.main import main
    from app.routes.admin import admin

    app.register_blueprint(user, url_prefix='/api')
    app.register_blueprint(tourist, url_prefix='/api')
    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/api/admin')

    return app
