from flask import Blueprint, redirect, render_template, request, session, url_for
import re
from sqlalchemy.exc import IntegrityError
from functools import wraps
from sqlalchemy import func
from alchemyClasses import db
from alchemyClasses.Curso import Curso
from alchemyClasses.Alumno import Alumno
from alchemyClasses.Profesor import Profesor
from alchemyClasses.Usuario import Usuario
from alchemyClasses.CursoAlumno import CursoAlumno
from alchemyClasses.Material import Material
from alchemyClasses.CursoMaterial import CursoMaterial
from werkzeug.utils import secure_filename
import os
from flask import current_app as app

alumno_bp = Blueprint("alumno", __name__, url_prefix="/alumno")

def alumno_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")

        if (
            not user
            or not isinstance(user, dict)
            or user.get("role") != "alumno"
        ):
            session.clear()
            return redirect(url_for("home.landing"))

        return f(*args, **kwargs)

    return decorated_function

@alumno_bp.route("/dashboard", methods=["GET"])
@alumno_required
def dashboard():
    """Panel de control del alumno"""
    return render_template("alumno-dashboard.html")

@alumno_bp.route("/cursos", methods=["GET"])
@alumno_required
def view_courses():
    """Ver cursos en los que el alumno está inscrito"""
    user = session.get("user")
    cursos = db.session.query(
        Curso.id_curso,
        Curso.nombre_curso,
        Curso.descripcion,
        Profesor.departamento,
        Usuario.nombre_usuario
    ).join(
        CursoAlumno, Curso.id_curso == CursoAlumno.id_curso
    ).join(
        Profesor, Curso.id_profesor == Profesor.id_profesor
    ).join(
        Usuario, Profesor.id_profesor == Usuario.id_usuario
    ).filter(
        CursoAlumno.id_alumno == user["id"]
    ).all()
    print(cursos)
    return render_template("alumno/cursos.html", cursos=cursos)


@alumno_bp.route("/inscribir/<int:curso_id>", methods=["POST"])
@alumno_required
def inscribir_curso(curso_id):
    user = session.get("user")
    curso = db.session.query(Curso).filter(Curso.id_curso == curso_id).first()

    if not curso:
        return "Curso no encontrado", 404

    # Verificar si el alumno ya está inscrito en el curso
    existing_inscription = db.session.query(CursoAlumno).filter(
        CursoAlumno.id_alumno == user["id"],
        CursoAlumno.id_curso == curso_id
    ).first()

    if not existing_inscription:
        new_inscription = CursoAlumno(id_alumno=user["id"], id_curso=curso_id, calificacion=None)
        db.session.add(new_inscription)

    db.session.commit()
    return redirect(url_for("alumno.view_courses"))

@alumno_bp.route("/desinscribir/<int:curso_id>", methods=["POST"])
@alumno_required
def desinscribir_curso(curso_id):
    user = session.get("user")
    inscription = db.session.query(CursoAlumno).filter(
        CursoAlumno.id_alumno == user["id"],
        CursoAlumno.id_curso == curso_id
    ).first()

    if inscription:
        db.session.delete(inscription)
        db.session.commit()

    return redirect(url_for("alumno.view_courses"))

@alumno_bp.route("/all-cursos", methods=["GET"])
@alumno_required
def all_cursos():
    """Ver todos los cursos disponibles para inscripción"""
    cursos = db.session.query(
        Curso.id_curso,
        Curso.nombre_curso,
        Curso.descripcion,
        Profesor.departamento,
        Usuario.nombre_usuario
    ).join(
        Profesor, Curso.id_profesor == Profesor.id_profesor
    ).join(
        Usuario, Profesor.id_profesor == Usuario.id_usuario
    ).outerjoin(
        CursoAlumno, (Curso.id_curso == CursoAlumno.id_curso) & (CursoAlumno.id_alumno == session.get("user")["id"])
    ).filter(
        CursoAlumno.id_curso == None  # Solo mostrar cursos en los que el alumno no está inscrito    
    ).all()

    return render_template("alumno/all_cursos.html", cursos=cursos)

@alumno_bp.route("/<int:curso_id>/calificación", methods=["GET"])
@alumno_required
def view_calificacion(curso_id):
    """Ver calificación del alumno en un curso específico"""
    user = session.get("user")
    curso_nombre = db.session.query(Curso.nombre_curso).filter(Curso.id_curso == curso_id).scalar()
    calificacion = db.session.query(CursoAlumno.calificacion).filter(
        CursoAlumno.id_alumno == user["id"],
        CursoAlumno.id_curso == curso_id
    ).scalar()

    return render_template("alumno/calificacion.html", calificacion=calificacion, curso_nombre=curso_nombre)    
    
@alumno_bp.route("/<int:curso_id>/materiales", methods=["GET"])
@alumno_required
def view_materiales(curso_id):
    """Ver materiales de un curso específico"""
    user = session.get("user")
    curso = db.session.query(Curso).filter(Curso.id_curso == curso_id).first()
    if not curso:
        return redirect(url_for("alumno.view_courses"))

    materiales = db.session.query(
        Material.id_material,
        Material.material,
        Material.descripcion
    ).join(
        CursoMaterial, Material.id_material == CursoMaterial.id_material
    ).filter(
        CursoMaterial.id_curso == curso_id
    ).all()

    return render_template("alumno/materiales.html", curso=curso, materiales=materiales)