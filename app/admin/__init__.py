from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps
from sqlalchemy import func
from alchemyClasses import db
from alchemyClasses.Curso import Curso
from alchemyClasses.Alumno import Alumno
from alchemyClasses.Profesor import Profesor
from alchemyClasses.Usuario import Usuario
from alchemyClasses.CursoAlumno import CursoAlumno

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")
        if not user or user.get("role") != "admin":
            return redirect(url_for("home.landing"))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    """Panel de control del administrador"""
    return render_template("admin-dashboard.html")


@admin_bp.route("/todos", methods=["GET"])
@admin_required
def view_all():
    """Vista de prueba para mostrar todos los usuarios, alumnos y profesores"""
    usuarios = Usuario.query.all()
    alumnos = Alumno.query.all()
    profesores = Profesor.query.all()
    return render_template("admin/todos.html", usuarios=usuarios, alumnos=alumnos, profesores=profesores)


@admin_bp.route("/cursos", methods=["GET"])
@admin_required
def view_courses():
    """Ver todos los cursos con información de profesor e inscritos"""
    cursos = db.session.query(
        Curso.id_curso,
        Curso.nombre_curso,
        Curso.descripcion,
        Profesor.id_profesor,
        Usuario.nombre_usuario,
        func.count(CursoAlumno.id_curso).label("total_alumnos")
    ).join(
        Profesor, Curso.id_profesor == Profesor.id_profesor
    ).join(
        Usuario, Profesor.id_profesor == Usuario.id_usuario
    ).outerjoin(
        CursoAlumno, Curso.id_curso == CursoAlumno.id_curso
    ).group_by(
        Curso.id_curso,
        Profesor.id_profesor,
        Usuario.nombre_usuario
    ).all()

    return render_template("admin/cursos.html", cursos=cursos)


@admin_bp.route("/alumnos", methods=["GET"])
@admin_required
def view_students():
    """Ver todos los alumnos registrados"""
    alumnos = db.session.query(
        Alumno.id_alumno,
        Usuario.nombre_usuario,
        Alumno.num_cuenta,
        Alumno.carrera,
        func.count(CursoAlumno.id_curso).label("total_cursos")
    ).join(
        Usuario, Alumno.id_alumno == Usuario.id_usuario
    ).outerjoin(
        CursoAlumno, Alumno.id_alumno == CursoAlumno.id_alumno
    ).group_by(
        Alumno.id_alumno
    ).all()

    return render_template("admin/alumnos.html", alumnos=alumnos)


@admin_bp.route("/cursos/<int:curso_id>/alumnos", methods=["GET"])
@admin_required
def view_course_students(curso_id):
    """Ver todos los alumnos inscritos en un curso específico"""
    curso = db.session.query(Curso).filter_by(id_curso=curso_id).first()
    
    if not curso:
        return render_template("admin/error.html", message="Curso no encontrado"), 404

    alumnos = db.session.query(
        Alumno.id_alumno,
        Usuario.nombre_usuario,
        Alumno.num_cuenta,
        Alumno.carrera
    ).join(
        CursoAlumno, Alumno.id_alumno == CursoAlumno.id_alumno
    ).join(
        Usuario, Alumno.id_alumno == Usuario.id_usuario
    ).filter(
        CursoAlumno.id_curso == curso_id
    ).all()

    return render_template(
        "admin/curso-alumnos.html",
        curso=curso,
        alumnos=alumnos
    )


@admin_bp.route("/profesores", methods=["GET"])
@admin_required
def view_teachers():
    """Ver todos los profesores y los cursos que imparten"""
    profesores = db.session.query(
        Profesor.id_profesor,
        Usuario.nombre_usuario,
        Profesor.num_empleado,
        Profesor.departamento,
        func.count(Curso.id_curso).label("total_cursos")
    ).join(
        Usuario, Profesor.id_profesor == Usuario.id_usuario
    ).outerjoin(
        Curso, Profesor.id_profesor == Curso.id_profesor
    ).group_by(
        Profesor.id_profesor
    ).all()

    return render_template("admin/profesores.html", profesores=profesores)


@admin_bp.route("/profesores/<int:profesor_id>/cursos", methods=["GET"])
@admin_required
def view_teacher_courses(profesor_id):
    """Ver todos los cursos que imparte un profesor específico"""
    profesor = db.session.query(Profesor).filter_by(id_profesor=profesor_id).first()
    
    if not profesor:
        return render_template("admin/error.html", message="Profesor no encontrado"), 404

    user = db.session.query(Usuario).filter_by(id_usuario=profesor_id).first()

    cursos = db.session.query(
        Curso.id_curso,
        Curso.nombre_curso,
        Curso.descripcion,
        func.count(CursoAlumno.id_curso).label("total_alumnos")
    ).filter(
        Curso.id_profesor == profesor_id
    ).outerjoin(
        CursoAlumno, Curso.id_curso == CursoAlumno.id_curso
    ).group_by(
        Curso.id_curso
    ).all()

    return render_template(
        "admin/profesor-cursos.html",
        cursos=cursos
    )