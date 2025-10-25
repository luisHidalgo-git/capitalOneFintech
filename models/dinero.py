# models/dinero.py
from __future__ import annotations
from . import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Numeric

class Dinero(db.Model):
    __tablename__ = "dinero"

    idDinero = db.Column(db.Integer, primary_key=True)
    saldo = db.Column(Numeric(12, 2), nullable=False, default=0)
    idUser = db.Column(db.Integer, ForeignKey("users.idUser"), nullable=False, index=True)

    user = relationship("User", back_populates="dinero")
    historial = relationship("Historial", back_populates="dinero", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dinero {self.idDinero} saldo={self.saldo}>"
