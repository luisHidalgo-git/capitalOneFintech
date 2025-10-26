from decimal import Decimal
from models import db
from models.dinero import Dinero
from models.user import User


class BalanceService:
    @staticmethod
    def get_balance_by_user(user_id: int) -> Dinero:
        return Dinero.query.filter_by(idUser=user_id).first()

    @staticmethod
    def create_balance(user_id: int, saldo_inicial: float = 0) -> Dinero:
        dinero = Dinero(
            saldo=max(0, saldo_inicial),
            deuda_credito=0,
            idUser=user_id
        )
        db.session.add(dinero)
        return dinero

    @staticmethod
    def update_balance(dinero: Dinero, monto: float, tipo: str) -> None:
        if tipo == "debito":
            current_saldo = float(dinero.saldo or 0)
            if current_saldo < monto:
                raise ValueError("Saldo insuficiente")
            nuevo_saldo = current_saldo - monto
            dinero.saldo = Decimal(str(nuevo_saldo))
        elif tipo == "credito":
            current_deuda = float(dinero.deuda_credito or 0)
            nueva_deuda = current_deuda + monto
            dinero.deuda_credito = Decimal(str(nueva_deuda))

        db.session.flush()

    @staticmethod
    def pay_credit_card(dinero: Dinero, monto: float) -> dict:
        saldo_actual = float(dinero.saldo or 0)
        deuda_actual = float(dinero.deuda_credito or 0)

        if deuda_actual <= 0:
            raise ValueError("No hay deuda de tarjeta")
        if saldo_actual <= 0:
            raise ValueError("Saldo insuficiente")

        pagable = min(monto, saldo_actual, deuda_actual)
        ajustado = pagable < monto

        dinero.saldo = Decimal(str(saldo_actual - pagable))
        dinero.deuda_credito = Decimal(str(deuda_actual - pagable))

        return {
            "pagable": pagable,
            "ajustado": ajustado,
            "nuevo_saldo": float(dinero.saldo),
            "nueva_deuda": float(dinero.deuda_credito)
        }

    @staticmethod
    def get_balance_info(user_id: int) -> dict:
        dinero = BalanceService.get_balance_by_user(user_id)
        if not dinero:
            raise ValueError("Saldo no encontrado")

        return {
            "idUser": user_id,
            "saldo": float(dinero.saldo or 0),
            "deuda_credito": float(dinero.deuda_credito or 0),
            "moneda": getattr(dinero, "moneda", "MXN") or "MXN"
        }
