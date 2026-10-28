from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from ..models import Service, Category
from .. import db

services = Blueprint("services", __name__)


@services.route("/services")
def browse():
    query = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)
    city = request.args.get("city", "").strip()
    sort = request.args.get("sort", "newest")

    results = Service.query.filter_by(status="approved")

    if query:
        results = results.filter(Service.title.ilike(f"%{query}%"))

    if category_id:
        results = results.filter_by(category_id=category_id)

    if city:
        results = results.filter(Service.city.ilike(f"%{city}%"))

    if sort == "price_low":
        results = results.order_by(Service.price.asc())
    elif sort == "price_high":
        results = results.order_by(Service.price.desc())
    else:
        results = results.order_by(Service.created_at.desc())

    categories = Category.query.order_by(Category.name).all()

    return render_template(
        "services.html",
        services=results.all(),
        categories=categories,
        selected_category=category_id,
        query=query,
        city=city,
        sort=sort,
    )


@services.route("/services/<int:service_id>")
def detail(service_id):
    service = Service.query.get_or_404(service_id)

    if service.status != "approved":
        flash("This service is not available.")
        return redirect(url_for("services.browse"))

    return render_template("service_detail.html", service=service)


@services.route("/services/add", methods=["GET", "POST"])
@login_required
def add():
    if current_user.role != "provider":
        flash("Only service providers can add services.")
        return redirect(url_for("main.home"))

    if request.method == "POST":
        price = request.form.get("price")

        service = Service(
            provider_id=current_user.id,
            category_id=request.form["category_id"],
            title=request.form["title"].strip(),
            description=request.form["description"].strip(),
            city=request.form["city"].strip(),
            price_type=request.form["price_type"],
            price=float(price) if price else None,
            status="pending",
        )

        db.session.add(service)
        db.session.commit()
        flash("Service submitted. Waiting for admin approval.")
        return redirect(url_for("services.my_services"))

    categories = Category.query.order_by(Category.name).all()
    return render_template("add_service.html", categories=categories)


@services.route("/my-services")
@login_required
def my_services():
    if current_user.role != "provider":
        flash("Only service providers can view this page.")
        return redirect(url_for("main.home"))

    services = Service.query.filter_by(provider_id=current_user.id).all()
    return render_template("my_services.html", services=services)