from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from alchemyClasses import db


class Curso(db.Model):
    __tablename__ = "Curso"

    id_curso = db.Column(db.Integer, primary_key=True)
    nombre_curso = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255))

    id_profesor = db.Column(
        db.Integer,
        db.ForeignKey("Profesor.id_profesor")
    )

    alumnos = db.relationship("CursoAlumno", backref="curso")
    materiales = db.relationship("CursoMaterial", backref="curso")

    def __init__(self, nombre_curso, descripcion, id_profesor):
        self.nombre_curso = nombre_curso
        self.descripcion = descripcion
        self.id_profesor = id_profesor

    def __str__(self):
        return f'Curso: {self.nombre_curso}\nProfesor ID: {self.id_profesor}'