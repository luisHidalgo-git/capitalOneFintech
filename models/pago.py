# models/pago.py
from . import db, TimeStampedMixin
from sqlalchemy.sql import func
from sqlalchemy import CheckConstraint, Index

class Pago(db.Model, TimeStampedMixin):
    __tablename__ = "pagos"
    idPago = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey("users.idUser"), nullable=False)
    motivo = db.Column(db.String(200), nullable=False)
    pagoFecha = db.Column(db.Date, nullable=False, server_default=func.current_date())
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    # tipo (debito|credito)
    tipo = db.Column(db.String(10), nullable=False, default="debito")

    __table_args__ = (
        CheckConstraint("tipo IN ('debito','credito')", name="ck_pagos_tipo"),
        Index("ix_pagos_user_fecha", "idUser", "pagoFecha"),
        Index("ix_pagos_tipo", "tipo"),
    )
