from flask import Blueprint, redirect, render_template, request, session, url_for
import re
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from alchemyClasses import db
from alchemyClasses.Administrador import Administrador
from alchemyClasses.Alumno import Alumno
from alchemyClasses.Profesor import Profesor
from alchemyClasses.Usuario import Usuario

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

VALID_ROLES = {"alumno", "profesor", "admin"}
VALID_DEPARTMENTS = {"ingles", "frances", "italiano", "aleman"}
VALID_CAREERS = {"matematicas", "computacion", "actuaria", "fisica"}


def _is_ten_digits(value):
    return bool(re.fullmatch(r"\d{10}", value))


def _build_role_entity(role, user_id, form):
    if role == "alumno":
        num_cuenta = form.get("num_cuenta", "").strip()
        carrera = form.get("carrera", "").strip().lower()

        if not _is_ten_digits(num_cuenta):
            return None, "El numero de cuenta del alumno debe tener exactamente 10 digitos."

        if carrera not in VALID_CAREERS:
            return None, "La carrera del alumno debe ser: matematicas, computacion, actuaria o fisica."

        return Alumno(
            id_alumno=user_id,
            num_cuenta=int(num_cuenta),
            carrera=carrera,
        ), None

    num_empleado = form.get("num_empleado", "").strip()
    departamento = form.get("departamento", "").strip().lower()
    if not num_empleado.isdigit() or not departamento:
        return None, "Para profesor/admin, captura num_empleado numerico y departamento."

    if role == "profesor":
        if not _is_ten_digits(num_empleado):
            return None, "El numero de empleado del profesor debe tener exactamente 10 digitos."

        if departamento not in VALID_DEPARTMENTS:
            return None, "El departamento del profesor debe ser: ingles, frances, italiano o aleman."

        return Profesor(
            id_profesor=user_id,
            num_empleado=int(num_empleado),
            departamento=departamento,
        ), None



@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return render_template(
                "login.html",
                error="Usuario o contrasena invalido."
            ), 400

        user = Usuario.query.filter_by(nombre_usuario=username).first()
        if not user or not check_password_hash(user.contrasena_usuario, password):
            return render_template("login.html", error="Credenciales invalidas."), 401

        user_role = (user.rol or "").strip().lower()
        if user_role not in VALID_ROLES:
            return render_template("login.html", error="Tu cuenta no tiene un rol valido."), 403

        session["user"] = {
            "id": user.id_usuario,
            "username": user.nombre_usuario,
            "role": user_role,
        }
        return redirect(url_for("role_views.dashboard"))

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "").strip().lower()

        if not username or not password or role not in VALID_ROLES:
            return render_template(
                "register.html",
                error="Completa todos los campos y selecciona un rol valido."
            ), 400

        if len(username) < 3:
            return render_template("register.html", error="El nombre de usuario debe tener al menos 3 caracteres."), 400

        if len(password) < 8:
            return render_template("register.html", error="La contrasena debe tener al menos 8 caracteres."), 400

        existing_user = Usuario.query.filter_by(nombre_usuario=username).first()
        if existing_user:
            return render_template("register.html", error="Ese nombre de usuario ya existe."), 409

        role_entity, role_error = _build_role_entity(role, user_id=0, form=request.form)
        if role_error:
            return render_template("register.html", error=role_error), 400

        user = Usuario(
            nombre_usuario=username,
            contrasena_usuario=generate_password_hash(password),
            rol=role,
        )

        try:
            db.session.add(user)
            db.session.flush()

            role_entity, _ = _build_role_entity(role, user_id=user.id_usuario, form=request.form)
            db.session.add(role_entity)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return render_template(
                "register.html",
                error="No se pudo crear la cuenta por conflicto de datos.",
            ), 409
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear usuario: {e}")
            return render_template(
                "register.html",
                error="No se pudo crear la cuenta. Intenta nuevamente.",
            ), 500

        session["user"] = {
            "id": user.id_usuario,
            "username": user.nombre_usuario,
            "role": user.rol,
        }
        return redirect(url_for("role_views.dashboard"))

    return render_template("register.html")

from flask import render_template, request, redirect, url_for, session
from alchemyClasses import db
from alchemyClasses.Usuario import Usuario

@auth_bp.route("/perfil", methods=["GET", "POST"])
def perfil():

    user_session = session.get("user")

    if not user_session:
        return redirect(url_for("auth.login"))

    usuario = Usuario.query.get(user_session["id"])

    if request.method == "POST":

        nuevo_nombre = request.form.get("nombre_usuario", "").strip()

        if not nuevo_nombre:
            return render_template(
                "perfil.html",
                usuario=usuario,
                error="El nombre no puede estar vacío."
            )

        usuario.nombre_usuario = nuevo_nombre

        db.session.commit()

        # actualizar sesión
        session["user"]["username"] = nuevo_nombre

        return render_template(
            "perfil.html",
            usuario=usuario,
            success="Perfil actualizado correctamente."
        )

    return render_template("perfil.html", usuario=usuario)

@auth_bp.route("/logout")
def logout():
    session.clear()  # Limpia toda la sesión para mayor seguridad
    session.pop("user", None)
    return redirect(url_for("home.landing"))
