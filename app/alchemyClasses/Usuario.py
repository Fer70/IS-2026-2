from sqlalchemy import Column, Integer, String
from alchemyClasses import db


class Usuario(db.Model):
    __tablename__ = 'Usuario'
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario = Column(String, nullable=False, unique=True)
    contrasena_usuario = Column(String, nullable=False)
    rol = Column(String, nullable=False)


    def __init__(self, nombre_usuario, contrasena_usuario, rol):
        self.nombre_usuario = nombre_usuario
        self.contrasena_usuario = contrasena_usuario
        self.rol = rol

    def __str__(self):
        return f'User: {self.nombre_usuario}\nRol: {self.rol}'