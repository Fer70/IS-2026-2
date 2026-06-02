from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from alchemyClasses import db

class CursoAlumno(db.Model):
    __tablename__ = "curso_alumno"

    id_alumno = db.Column(
        db.Integer,
        db.ForeignKey("Alumno.id_alumno"),
        primary_key=True
    )

    id_curso = db.Column(
        db.Integer,
        db.ForeignKey("Curso.id_curso"),
        primary_key=True
    )

    calificacion = db.Column(db.Float)

    def __init__(self, id_alumno, id_curso, calificacion):
        self.id_alumno = id_alumno
        self.id_curso = id_curso
        self.calificacion = calificacion
    def __str__(self):
        return f"CursoAlumno: Alumno ID: {self.id_alumno}, Curso ID: {self.id_curso}, Calificación: {self.calificacion}"