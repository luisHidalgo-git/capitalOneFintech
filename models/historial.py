# models/historial.py
from . import db
from sqlalchemy.sql import func

class Historial(db.Model):
    __tablename__ = "historial"
    idHistorial = db.Column(db.Integer, primary_key=True)
    idDinero = db.Column(db.Integer, db.ForeignKey("dinero.idDinero"), nullable=False)
    idPago = db.Column(db.Integer, db.ForeignKey("pagos.idPago"), nullable=False)

    pago = db.relationship("Pago", backref="historial_items", lazy=True)
    dinero = db.relationship("Dinero", backref="historial_items", lazy=True)

    # NUEVO: auditoría
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        db.Index("idx_historial_dinero", "idDinero"),
        db.Index("idx_historial_pago", "idPago"),
    )
