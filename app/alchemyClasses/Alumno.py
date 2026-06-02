from sqlalchemy import Column, Integer, String, BigInteger
from alchemyClasses import db

class Alumno(db.Model):
    __tablename__ = 'Alumno'
    id_alumno = Column(Integer, db.ForeignKey("Usuario.id_usuario"), primary_key=True)
    num_cuenta = Column(BigInteger, nullable=False)
    carrera = Column(String, nullable=False)


    def __init__(self, id_alumno, num_cuenta, carrera):
        self.id_alumno = id_alumno
        self.num_cuenta = num_cuenta    
        self.carrera = carrera

    def __str__(self):
        return f'Alumno: {self.num_cuenta}\nCarrera: {self.carrera}'