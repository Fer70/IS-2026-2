from sqlalchemy import Column, Integer, String, BigInteger
from alchemyClasses import db

class Profesor(db.Model):
    __tablename__ = 'Profesor'
    id_profesor = Column(Integer, db.ForeignKey("Usuario.id_usuario"), primary_key=True)
    num_empleado = Column(BigInteger, nullable=False)
    departamento = Column(String, nullable=False)



    def __init__(self, id_profesor, num_empleado, departamento):
        self.id_profesor = id_profesor
        self.num_empleado = num_empleado
        self.departamento = departamento

    def __str__(self):
        return f'Profesor: {self.num_empleado}, Departamento: {self.departamento}'