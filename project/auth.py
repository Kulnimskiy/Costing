from flask import Blueprint, render_template, request, redirect, session

auth = Blueprint("auth", __name__)

users = []
regestered = []


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        company_name_ = request.form.get("company_name")
        company_inn_ = request.form.get("company_inn")
        login_ = request.form.get("login")
        email_ = request.form.get("email")
        password_ = request.form.get("password")
        password_confirm_ = request.form.get("password_confirm")
        if not all([company_name_, company_inn_, login_, email_, password_, password_confirm_]):
            return render_template("signup.html", error="Fill in all the fields")
        if password_confirm_ != password_:
            return render_template("signup.html", error="Passwords are different")
        regestered.append({"company_name": company_name_,
                           "company_inn": company_inn_,
                           "login": login_,
                           "email": email_,
                           "password": password_})
        print(regestered, session.get("user"))
        return redirect("/login")
    return render_template("signup.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_ = request.form.get("login")
        password_ = request.form.get("password")
        session["user"] = login_
        if not login_ or not password_:
            return render_template("login.html", error="incorrect login or password")
        users.append((login_, password_))
        print(users, session.get("user"))
        return redirect("/")
    else:
        return render_template("login.html")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
