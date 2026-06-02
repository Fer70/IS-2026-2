from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from alchemyClasses import db

class CursoMaterial(db.Model):
    __tablename__ = "curso_material"

    id_curso = db.Column(
        db.Integer,
        db.ForeignKey("Curso.id_curso"),
        primary_key=True
    )

    id_material = db.Column(
        db.Integer,
        db.ForeignKey("Material.id_material"),
        primary_key=True
    )
     
    def __init__(self, id_curso, id_material):
        self.id_curso = id_curso
        self.id_material = id_material
    def __str__(self):
        return f"CursoMaterial: Curso ID: {self.id_curso}, Material ID: {self.id_material}"