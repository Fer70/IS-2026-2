from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from alchemyClasses import db

class NombreCompleto(db.Model):
    __tablename__ = "nombre_completo"

    id_nombre_completo = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellido = db.Column(db.String(255), nullable=False)

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("Usuario.id_usuario")
    )

    def __init__(self, nombre, apellido, id_usuario):
        self.nombre = nombre
        self.apellido = apellido
        self.id_usuario = id_usuario
    def __str__(self):
        return f"NombreCompleto: {self.nombre} {self.apellido}, Usuario ID: {self.id_usuario}"