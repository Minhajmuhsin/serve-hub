from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from ..models import User
from .. import db

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form.get("role", "customer")

        if role not in ["customer", "provider"]:
            role = "customer"

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("This email is already registered.")
            return redirect(url_for("auth.register"))

        user = User(
            name=name,
            email=email,
            role=role,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Account created successfully.")
        return redirect(url_for("main.home"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for("main.home"))

        flash("Invalid email or password.")

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.home"))