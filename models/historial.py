# models/historial.py
from __future__ import annotations
from . import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Historial(db.Model):
    __tablename__ = "historial"

    idHistorial = db.Column(db.Integer, primary_key=True)
    idDinero = db.Column(db.Integer, ForeignKey("dinero.idDinero"), nullable=False, index=True)
    idPago = db.Column(db.Integer, ForeignKey("pagos.idPago"), nullable=False, index=True)

    # Relaciones
    dinero = relationship("Dinero", back_populates="historial")
    pago = relationship("Pago", back_populates="historial")

    def __repr__(self):
        return f"<Historial {self.idHistorial} d={self.idDinero} p={self.idPago}>"
