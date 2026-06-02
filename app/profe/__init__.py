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
from alchemyClasses.CursoMaterial import CursoMaterial
from alchemyClasses.Material import Material
from werkzeug.utils import secure_filename
import os
from flask import current_app as app


profe_bp = Blueprint("profe", __name__, url_prefix="/profe")

def profesor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")

        if (
            not user
            or not isinstance(user, dict)
            or user.get("role") != "profesor"
        ):
            session.clear()
            return redirect(url_for("home.landing"))

        return f(*args, **kwargs)

    return decorated_function

@profe_bp.route("/dashboard", methods=["GET"])
@profesor_required
def dashboard():
    """Panel de control del profesor"""
    return render_template("profesor-dashboard.html")


@profe_bp.route("/cursos", methods=["GET"])
@profesor_required
def view_courses():
    """Ver cursos del profesor con información de inscritos"""
    user = session.get("user")
    cursos = db.session.query(
        Curso.id_curso,
        Curso.nombre_curso,
        Curso.descripcion,
        func.count(CursoAlumno.id_curso).label("total_alumnos")
    ).filter(
        Curso.id_profesor == user["id"]
    ).outerjoin(
        CursoAlumno, Curso.id_curso == CursoAlumno.id_curso
    ).group_by(
        Curso.id_curso
    ).all()

    return render_template("profe/cursos.html", cursos=cursos)

@profe_bp.route("/alumnos/<int:curso_id>", methods=["GET"])
@profesor_required
def view_students(curso_id):
    """Ver alumnos inscritos en un curso específico del profesor"""
    user = session.get("user")
    curso = Curso.query.filter_by(id_curso=curso_id, id_profesor=user["id"]).first()
    if not curso:
        return redirect(url_for("profe.view_courses"))

    alumnos = db.session.query(
        Alumno.id_alumno,
        Alumno.num_cuenta,
        Alumno.carrera,
        Usuario.nombre_usuario
    ).join(
        CursoAlumno, Alumno.id_alumno == CursoAlumno.id_alumno
    ).join(
        Usuario, Alumno.id_alumno == Usuario.id_usuario
    ).filter(
        CursoAlumno.id_curso == curso_id
    ).all()

    return render_template("profe/alumnos.html", curso=curso, alumnos=alumnos)

@profe_bp.route("/crear", methods=["GET", "POST"])
@profesor_required
def create_course():
    """Vista para crear un nuevo curso (opcional)"""
    if request.method == "POST":
        user = session.get("user")
        nombre_curso = request.form.get("nombre_curso", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if not nombre_curso:
            return render_template(
                "profe/crear_curso.html",
                error="El nombre del curso es obligatorio."
            ), 400

        nuevo_curso = Curso(
            nombre_curso=nombre_curso,
            descripcion=descripcion,
            id_profesor=user["id"]
        )
        db.session.add(nuevo_curso)
        db.session.commit()
        return redirect(url_for("profe.view_courses"))
    return render_template("profe/crear_curso.html")

@profe_bp.route("/upload_material/<int:curso_id>", methods=["GET", "POST"])
@profesor_required
def upload_material(curso_id):  
    """Vista para subir materiales a un curso específico"""
    user = session.get("user")
    curso = Curso.query.filter_by(id_curso=curso_id, id_profesor=user["id"]).first()
    if not curso:
        return redirect(url_for("profe.view_courses"))

    if request.method == "POST":
        archivo = request.files.get("pdf")
        if not archivo or archivo.filename == "":
            return render_template(
                "profe/upload_material.html",
                curso=curso,
                error="No se ha seleccionado ningún archivo."
            ), 400
        filename = secure_filename(archivo.filename)
        ruta = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        archivo.save(ruta)
        nuevo_material = Material(
            material=filename,
            descripcion=request.form.get("descripcion", "").strip()
        )
        db.session.add(nuevo_material)
        db.session.commit()
        curso_material = CursoMaterial(
            id_curso=curso_id,
            id_material=nuevo_material.id_material
        )
        db.session.add(curso_material)
        db.session.commit()
        return redirect(url_for("profe.view_courses"))
    materiales = db.session.query(
        Material.id_material,
        Material.material,
        Material.descripcion
    ).join(
        CursoMaterial, Material.id_material == CursoMaterial.id_material
    ).filter(
        CursoMaterial.id_curso == curso_id
    ).all()
    return render_template("profe/upload_material.html", curso=curso, materiales=materiales)    

@profe_bp.route("/delete_material/<int:curso_id>/<int:material_id>", methods=["POST"])
@profesor_required
def delete_material(curso_id, material_id):
    """Vista para eliminar un material de un curso específico"""
    user = session.get("user")
    curso = Curso.query.filter_by(id_curso=curso_id, id_profesor=user["id"]).first()
    if not curso:
        return redirect(url_for("profe.view_courses"))

    material = Material.query.filter_by(id_material=material_id).first()
    if not material:
        return redirect(url_for("profe.view_courses"))

    CursoMaterial.query.filter_by(id_material=material_id).delete()
    db.session.delete(material)
    db.session.commit()
    return redirect(url_for("profe.upload_material", curso_id=curso_id))

@profe_bp.route("/delete_course/<int:curso_id>", methods=["POST"])
@profesor_required
def delete_course(curso_id):
    """Vista para eliminar un curso específico del profesor"""
    user = session.get("user")
    curso = Curso.query.filter_by(id_curso=curso_id, id_profesor=user["id"]).first()
    if not curso:
        return redirect(url_for("profe.view_courses"))
    materiales = db.session.query(CursoMaterial.id_material).filter_by(id_curso=curso_id).all()
    for material in materiales:
        CursoMaterial.query.filter_by(id_material=material.id_material).delete()
        Material.query.filter_by(id_material=material.id_material).delete()
    CursoAlumno.query.filter_by(id_curso=curso_id).delete()
    CursoMaterial.query.filter_by(id_curso=curso_id).delete()
    db.session.delete(curso)
    db.session.commit()
    return redirect(url_for("profe.view_courses"))

@profe_bp.route("/<int:curso_id>/<int:alumno_id>/calificar", methods=["GET", "POST"])
@profesor_required
def calificar_alumno(curso_id, alumno_id):
    """Vista para calificar a un alumno en un curso específico"""
    user = session.get("user")
    curso = Curso.query.filter_by(id_curso=curso_id, id_profesor=user["id"]).first()
    if not curso:
        return redirect(url_for("profe.view_courses"))

    alumno = Alumno.query.filter_by(id_alumno=alumno_id).first()
    if not alumno:
        return redirect(url_for("profe.view_students", curso_id=curso_id))
    
    # Obtener la calificación actual de la base de datos
    curso_alumno = CursoAlumno.query.filter_by(id_curso=curso_id, id_alumno=alumno_id).first()
    calificacion_actual = f"{curso_alumno.calificacion:.2f}" if curso_alumno and curso_alumno.calificacion else None
    
    if request.method == "POST":
        calificacion = request.form.get("calificacion")
        if not calificacion:
            return render_template("profe/calificar_alumno.html", curso=curso, alumno=alumno, calificacion=calificacion_actual, error="Por favor, ingresa una calificación.")
        try:
            calificacion = float(calificacion)
            if not 0 <= calificacion <= 100:
                raise ValueError("La calificación debe estar entre 0 y 100.")
        except ValueError as e:
            return render_template("profe/calificar_alumno.html", curso=curso, alumno=alumno, calificacion=calificacion_actual, error=str(e))
        
        if not curso_alumno:
            return render_template("profe/calificar_alumno.html", curso=curso, alumno=alumno, calificacion=calificacion_actual, error="El alumno no está inscrito en este curso.")
        
        curso_alumno.calificacion = calificacion
        db.session.commit()
        return redirect(url_for("profe.view_students", curso_id=curso_id))
    
    return render_template("profe/calificar_alumno.html", curso=curso, alumno=alumno, calificacion=calificacion_actual)
