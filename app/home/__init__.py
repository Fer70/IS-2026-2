from flask import Blueprint, render_template, session

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def landing():
    session.clear()  # Limpia toda la sesión para mayor seguridad
    session.pop("user", None)
    return render_template("landing.html")

@home_bp.route("/about")
def about():
    return render_template("about.html")
