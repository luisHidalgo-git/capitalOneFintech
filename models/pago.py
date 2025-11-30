# models/pago.py
from . import db, TimeStampedMixin
from sqlalchemy.sql import func
from sqlalchemy import CheckConstraint, Index
from datetime import date

class Pago(db.Model, TimeStampedMixin):
    __tablename__ = "pagos"
    idPago = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey("users.idUser"), nullable=False)
    motivo = db.Column(db.String(200), nullable=False)
    # Use a Python-side default to avoid emitting a MySQL-incompatible
    # DDL like `DEFAULT CURRENT_DATE` on some MySQL versions.
    # SQLAlchemy will then set the value at insert time instead of
    # creating a table DEFAULT constraint.
    pagoFecha = db.Column(db.Date, nullable=False, default=date.today)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    # tipo (debito|credito)
    tipo = db.Column(db.String(10), nullable=False, default="debito")
    # metadata / optional fields
    categoria = db.Column(db.String(60), nullable=True)
    metodo = db.Column(db.String(20), nullable=True)
    referencia = db.Column(db.String(80), nullable=True)
    notas = db.Column(db.Text, nullable=True)

    __table_args__ = (
        CheckConstraint("tipo IN ('debito','credito')", name="ck_pagos_tipo"),
        Index("ix_pagos_user_fecha", "idUser", "pagoFecha"),
        Index("ix_pagos_tipo", "tipo"),
    )
