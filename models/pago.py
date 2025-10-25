# models/pago.py
from __future__ import annotations
from . import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Numeric, Date

class Pago(db.Model):
    __tablename__ = "pagos"

    idPago = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, ForeignKey("users.idUser"), nullable=False, index=True)
    motivo = db.Column(db.String(200), nullable=False)
    pagoFecha = db.Column(Date, nullable=False)
    monto = db.Column(Numeric(12, 2), nullable=False)

    # Relaciones
    user = relationship("User", back_populates="pagos")
    historial = relationship("Historial", back_populates="pago", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Pago {self.idPago} monto={self.monto}>"
