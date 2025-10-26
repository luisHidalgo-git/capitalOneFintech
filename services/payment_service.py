from datetime import date
from models import db
from models.pago import Pago
from models.historial import Historial
from models.dinero import Dinero
from services.balance_service import BalanceService


class PaymentService:
    @staticmethod
    def register_payment(user_id: int, motivo: str, monto: float, tipo: str = "debito",
                        categoria: str = None, metodo: str = None,
                        referencia: str = None, notas: str = None) -> dict:

        if not motivo or monto is None:
            raise ValueError("Faltan datos requeridos (motivo, monto)")

        if monto <= 0:
            raise ValueError("Monto debe ser mayor a 0")

        if tipo not in ("debito", "credito"):
            raise ValueError("tipo debe ser 'debito' o 'credito'")

        dinero = BalanceService.get_balance_by_user(user_id)
        if not dinero:
            raise ValueError("No hay saldo asociado")

        BalanceService.update_balance(dinero, monto, tipo)

        try:
            pago = Pago(
                idUser=user_id,
                motivo=motivo,
                pagoFecha=date.today(),
                monto=monto,
                tipo=tipo,
                categoria=categoria,
                metodo=metodo,
                referencia=referencia,
                notas=notas
            )
            db.session.add(pago)
            db.session.flush()
        except Exception:
            db.session.rollback()
            pago = Pago(
                idUser=user_id,
                motivo=motivo,
                pagoFecha=date.today(),
                monto=monto,
                tipo=tipo
            )
            db.session.add(pago)
            db.session.flush()

        db.session.add(Historial(idDinero=dinero.idDinero, idPago=pago.idPago))

        return {
            "pago_id": pago.idPago,
            "tipo": tipo,
            "categoria": categoria,
            "metodo": metodo,
            "nuevo_saldo": float(dinero.saldo),
            "nueva_deuda_credito": float(dinero.deuda_credito or 0)
        }

    @staticmethod
    def pay_credit_card(user_id: int, monto: float) -> dict:
        if monto <= 0:
            raise ValueError("Monto debe ser mayor a 0")

        dinero = BalanceService.get_balance_by_user(user_id)
        if not dinero:
            raise ValueError("No hay saldo asociado")

        result = BalanceService.pay_credit_card(dinero, monto)

        pago = Pago(
            idUser=user_id,
            motivo="Pago tarjeta",
            pagoFecha=date.today(),
            monto=result["pagable"],
            tipo="debito"
        )
        db.session.add(pago)
        db.session.flush()

        db.session.add(Historial(idDinero=dinero.idDinero, idPago=pago.idPago))

        return {
            "mensaje": "Pago de tarjeta aplicado" + (" (ajustado)" if result["ajustado"] else ""),
            "monto_pagado": result["pagable"],
            "ajustado": result["ajustado"],
            "nuevo_saldo": result["nuevo_saldo"],
            "nueva_deuda_credito": result["nueva_deuda"],
            "pago_id": pago.idPago
        }

    @staticmethod
    def get_payments_by_user(user_id: int, dinero_id: int, page: int = 1,
                            per_page: int = 10, tipo: str = None) -> dict:
        base_q = (
            db.session.query(Pago)
            .join(Historial, Historial.idPago == Pago.idPago)
            .filter(Historial.idDinero == dinero_id)
        )

        if tipo in ("debito", "credito"):
            base_q = base_q.filter(Pago.tipo == tipo)

        total = base_q.count()
        items = (
            base_q.order_by(Pago.pagoFecha.desc(), Pago.idPago.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        movimientos = [{
            "motivo": p.motivo,
            "monto": float(p.monto),
            "signo": "-" if (p.tipo or "debito") == "debito" else "+",
            "fecha": p.pagoFecha.isoformat() if p.pagoFecha else None,
            "tipo": p.tipo or "debito",
            "categoria": getattr(p, "categoria", None),
            "metodo": getattr(p, "metodo", None),
        } for p in items]

        return {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
            "has_prev": page > 1,
            "has_next": page * per_page < total,
            "movimientos": movimientos
        }
