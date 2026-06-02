from functools import wraps

from flask import Blueprint, redirect, render_template, session, url_for

role_views_bp = Blueprint("role_views", __name__, url_prefix="/app")

TEMPLATE_BY_ROLE = {
    "admin": "role_views.admin_home",
    "profesor": "role_views.profesor_home",
    "alumno": "role_views.alumno_home",
}


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            user = session.get("user")
            if not user:
                return redirect(url_for("auth.login"))

            role = user.get("role", "").lower()
            if role not in roles:
                return render_template(
                    "error.html",
                    message="No tienes permisos para acceder a esta vista.",
                ), 403

            return view(*args, **kwargs)

        return wrapped_view

    return decorator


@role_views_bp.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    role = user.get("role", "").lower()
    endpoint = TEMPLATE_BY_ROLE.get(role)

    if not endpoint:
        return render_template(
            "error.html",
            message="Rol no soportado para vista de inicio."
        ), 403

    return redirect(url_for(endpoint))


@role_views_bp.route("/admin")
@role_required("admin")
def admin_home():
    return render_template("admin-dashboard.html", user=session.get("user"))


@role_views_bp.route("/profesor")
@role_required("profesor")
def profesor_home():
    return render_template("profesor-dashboard.html", user=session.get("user"))


@role_views_bp.route("/alumno")
@role_required("alumno")
def alumno_home():
    return render_template("alumno-dashboard.html", user=session.get("user"))
