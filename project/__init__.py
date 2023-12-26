from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # configure the app for the database use
    app.config["SECRET_KEY"] = "THEballisinTHEbasket"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    db.init_app(app)

    # add configuration to use sessions
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # auth routs will be processed here
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for the rest of the app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.after_request
    def after_request(response):
        """Ensure responses aren't cached"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    return app
