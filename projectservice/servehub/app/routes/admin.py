from ..models import User, Category, Service
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from ..models import User
from .. import db

admin = Blueprint("admin", __name__)


def admin_required():
    if not current_user.is_authenticated or current_user.role != "admin":
        flash("Admin access required.")
        return False
    return True


@admin.route("/admin")
@login_required
def dashboard():
    if not admin_required():
        return redirect(url_for("main.home"))

    customers = User.query.filter_by(role="customer").all()
    providers = User.query.filter_by(role="provider").all()

    return render_template(
        "admin/dashboard.html",
        customers=customers,
        providers=providers,
    )


@admin.route("/admin/users/<int:user_id>/verify", methods=["POST"])
@login_required
def verify_user(user_id):
    if not admin_required():
        return redirect(url_for("main.home"))

    user = db.session.get(User, user_id)

    if user:
        user.is_verified = True
        db.session.commit()
        flash(f"{user.name} has been verified.")

    return redirect(url_for("admin.dashboard"))


@admin.route("/admin/users/<int:user_id>/make-admin", methods=["POST"])
@login_required
def make_admin(user_id):
    if not admin_required():
        return redirect(url_for("main.home"))

    user = db.session.get(User, user_id)

    if user:
        user.role = "admin"
        db.session.commit()
        flash(f"{user.name} is now an admin.")

    return redirect(url_for("admin.dashboard"))
@admin.route("/admin/categories", methods=["GET", "POST"])
@login_required
def categories():
    if not admin_required():
        return redirect(url_for("main.home"))

    if request.method == "POST":
        name = request.form["name"].strip()
        slug = name.lower().replace(" ", "-")

        if name and not Category.query.filter_by(slug=slug).first():
            category = Category(name=name, slug=slug)
            db.session.add(category)
            db.session.commit()
            flash("Category added.")

        return redirect(url_for("admin.categories"))

    categories = Category.query.order_by(Category.name).all()
    return render_template("admin/categories.html", categories=categories)


@admin.route("/admin/services")
@login_required
def services():
    if not admin_required():
        return redirect(url_for("main.home"))

    services = Service.query.order_by(Service.created_at.desc()).all()
    return render_template("admin/services.html", services=services)


@admin.route("/admin/services/<int:service_id>/approve", methods=["POST"])
@login_required
def approve_service(service_id):
    if not admin_required():
        return redirect(url_for("main.home"))

    service = db.session.get(Service, service_id)

    if service:
        service.status = "approved"
        db.session.commit()
        flash("Service approved.")

    return redirect(url_for("admin.services"))


@admin.route("/admin/services/<int:service_id>/reject", methods=["POST"])
@login_required
def reject_service(service_id):
    if not admin_required():
        return redirect(url_for("main.home"))

    service = db.session.get(Service, service_id)

    if service:
        service.status = "rejected"
        db.session.commit()
        flash("Service rejected.")

    return redirect(url_for("admin.services"))