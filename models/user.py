# models/user.py
from __future__ import annotations
from . import db

class User(db.Model):
    __tablename__ = "users"

    idUser = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(190), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    biometricos = db.Column(db.String(255))
    numeroTelefono = db.Column(db.String(30))

    # Relaciones
    dinero = db.relationship("Dinero", back_populates="user", uselist=False)
    pagos = db.relationship("Pago", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.idUser} {self.correo}>"
