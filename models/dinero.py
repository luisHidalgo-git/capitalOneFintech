# models/dinero.py
from . import db
from sqlalchemy.sql import func

class Dinero(db.Model):
    __tablename__ = "dinero"
    idDinero = db.Column(db.Integer, primary_key=True)
    saldo = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    idUser = db.Column(db.Integer, db.ForeignKey("users.idUser"), nullable=False)

    # EXISTENTE: saldo usado de la tarjeta de crédito
    deuda_credito = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    # NUEVO: moneda + auditoría
    moneda = db.Column(db.String(3), nullable=False, default="MXN")
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        db.Index("idx_dinero_user", "idUser"),
    )
