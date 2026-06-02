from sqlalchemy import Column, Integer, String
from alchemyClasses import db

class Administrador(db.Model):
    __tablename__ = 'Administrador'
    id_administrador = Column(Integer, db.ForeignKey("Usuario.id_usuario"), primary_key=True)
    num_empleado = Column(Integer, nullable=False)
    departamento = Column(String, nullable=False)


    def __init__(self, id_administrador, num_empleado, departamento):
        self.id_administrador = id_administrador
        self.num_empleado = num_empleado
        self.departamento = departamento

    def __str__(self):
        return f'Administrador: {self.num_empleado}, Departamento: {self.departamento}'