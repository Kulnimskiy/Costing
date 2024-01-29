from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_login import LoginManager

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # configure the app for the database use
    app.config["SECRET_KEY"] = "THEballisinTHEbasket"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    # add configuration to use sessions
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # specifies user loader and tells Flask-Login how to find a specific user from the ID stored in their session cookie
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from project.models import User, Companies

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # auth routs will be processed here
    from project.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for the rest of the app
    from project.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.after_request
    def after_request(response):
        """Ensure responses aren't cached"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    return app
