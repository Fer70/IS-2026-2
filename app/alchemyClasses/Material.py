from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from alchemyClasses import db


class Material(db.Model):
    __tablename__ = "Material"

    id_material = db.Column(db.Integer, primary_key=True)
    material = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255))

    cursos = db.relationship("CursoMaterial", backref="material")

    def __init__(self, material, descripcion):
        self.material = material
        self.descripcion = descripcion
        
    def __str__(self):
        return f'Material: {self.material}\nDescripcion: {self.descripcion}'