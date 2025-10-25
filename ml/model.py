# ml/model.py
from __future__ import annotations

def evaluar_gasto(
    *,
    saldo: float,
    suscripciones: int,
    esencial: bool,
    nuevo_gasto: float,
    historial_pagos: list[dict] = None
) -> int:
    """
    Regresa 1 si el gasto es riesgoso, 0 si no.
    Ahora considera el historial de pagos del usuario para evaluar mejor.
    """
    if saldo is None or nuevo_gasto is None:
        return 1

    if saldo <= 0:
        return 1

    # Análisis del historial
    gasto_promedio = 0
    gasto_total_ultimos = 0
    gastos_similares = []

    if historial_pagos:
        montos = [p.get("monto", 0) for p in historial_pagos if p.get("monto")]
        if montos:
            gasto_promedio = sum(montos) / len(montos)
            # Últimos 5 pagos
            ultimos_pagos = montos[-5:]
            gasto_total_ultimos = sum(ultimos_pagos)

            # Gastos similares (mismo motivo o monto parecido)
            for pago in historial_pagos:
                if abs(pago.get("monto", 0) - nuevo_gasto) / max(nuevo_gasto, 1) < 0.2:
                    gastos_similares.append(pago.get("monto", 0))

    # Umbral base
    umbral = 0.35

    # Ajustes por tipo de gasto
    if not esencial:
        umbral -= 0.10

    # Ajustes por suscripciones
    extra_subs = max(0, suscripciones - 5)
    umbral -= 0.02 * extra_subs

    # Ajustes por historial
    if gasto_promedio > 0:
        # Si el nuevo gasto es mucho mayor al promedio, más riesgo
        if nuevo_gasto > gasto_promedio * 2:
            umbral -= 0.08
        # Si es menor al promedio, menos riesgo
        elif nuevo_gasto < gasto_promedio * 0.5:
            umbral += 0.05

    # Si hay gastos similares previos, es menos riesgoso
    if len(gastos_similares) >= 2:
        umbral += 0.05

    # Si ha gastado mucho recientemente, más estricto
    if gasto_total_ultimos > saldo * 0.6:
        umbral -= 0.10

    # Límites
    umbral = max(0.08, min(0.45, umbral))

    # Decisión
    ratio = nuevo_gasto / saldo
    return 1 if ratio >= umbral else 0
