from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from .helpers import password_checker, email_checker, inn_checker, login_checker

auth = Blueprint("auth", __name__)


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        company_name_ = request.form.get("company_name")

        # check if the company is already in the db
        company_inn_ = inn_checker(request.form.get("company_inn"))
        if not company_inn_:
            flash("Your inn isn' valid")
            return redirect("/signup")
        user_inn = User.query.filter_by(company_inn=company_inn_).first()
        if user_inn:
            flash("Your company has already signed up!")
            return redirect("/signup")

        # check if the user is already in the db
        login_ = request.form.get("login")
        user_login = User.query.filter_by(login=login_).first()
        if user_login:
            return render_template("signup.html", error="login already exists")

        # validate the email
        email_ = email_checker(request.form.get("email"))
        if not email_:
            return render_template("signup.html", error="Your email isn't valid")

        # check if the password satisfies the requirements
        password_ = password_checker(request.form.get("password"))
        password_confirm_ = password_checker(request.form.get("password_confirm"))
        if password_confirm_ != password_:
            return render_template("signup.html", error="Passwords are different")

        if not all([company_name_, company_inn_, login_, email_, password_, password_confirm_]):
            return render_template("signup.html", error="Fill in all the fields")

        # create a new user if everything has been filled correctly
        new_user = User(company_name=company_name_,
                        company_inn=company_inn_,
                        login=login_,
                        email=email_,
                        password=generate_password_hash(password_))

        # add the user to the db
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    return render_template("signup.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        login_ = login_checker(request.form.get("login"))
        password_ = request.form.get("password")
        remember = True if request.form.get("remember") else False
        user = User.query.filter_by(login=login_).first()
        if not login_ or not password_:
            return render_template("login.html", error="incorrect login or password")
        if not user or not check_password_hash(user.password, password_):
            return render_template("login.html", error="incorrect login or password")
        login_user(user, remember=remember)
        return redirect("/")
    else:
        return render_template("login.html")


@auth.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


@auth.route("/checklogin/<cur_login>")
def check_login(cur_login):
    cur_login = login_checker(cur_login)
    if not cur_login:
        return "1"  # the login doesn't satisfy the requirements
    if User.query.filter_by(login=cur_login).first():
        return "2"  # the login already exists
    return "0"  # the login is fine


@auth.route("/checkinn/<cur_inn>")
def check_inn(cur_inn):
    cur_inn = inn_checker(cur_inn)
    if not cur_inn:
        return "1"  # the inn doesn't satisfy the requirements
    if User.query.filter_by(company_inn=cur_inn).first():
        return "2"  # the inn already exists
    return "0"  # the inn is fine
