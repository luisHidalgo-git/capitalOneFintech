# ml/gpt.py
from __future__ import annotations
import os

def generar_mensaje_gpt(
    *,
    saldo: float,
    suscripciones: int,
    esencial: bool,
    nuevo_gasto: float,
    historial_pagos: list[dict] = None
) -> str:
    """
    Genera un mensaje personalizado con OpenAI basado en el historial del usuario.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _generar_mensaje_fallback(
            saldo=saldo,
            suscripciones=suscripciones,
            esencial=esencial,
            nuevo_gasto=nuevo_gasto,
            historial_pagos=historial_pagos
        )

    try:
        from openai import OpenAI
        client = OpenAI()

        # Análisis del historial
        contexto_historial = ""
        if historial_pagos and len(historial_pagos) > 0:
            total_pagos = len(historial_pagos)
            montos = [p.get("monto", 0) for p in historial_pagos]
            promedio = sum(montos) / len(montos) if montos else 0
            total_gastado = sum(montos)

            contexto_historial = (
                f"\n\nHistorial del usuario:\n"
                f"- Total de pagos realizados: {total_pagos}\n"
                f"- Gasto promedio: ${promedio:,.2f}\n"
                f"- Total gastado: ${total_gastado:,.2f}\n"
            )

            if total_pagos >= 3:
                ultimos_3 = historial_pagos[-3:]
                motivos = [p.get("motivo", "Sin motivo") for p in ultimos_3]
                contexto_historial += f"- Últimos gastos: {', '.join(motivos)}\n"

        prompt = (
            "Eres un asesor financiero personal y empático que conoce bien los hábitos del usuario. "
            "Basándote en su historial de gastos, proporciona un mensaje personalizado que:\n"
            "1. Reconozca sus patrones de gasto\n"
            "2. Explique por qué este gasto podría ser riesgoso AHORA\n"
            "3. Ofrezca 2-3 recomendaciones específicas y accionables\n"
            "4. Sea cercano pero profesional\n\n"
            f"Situación actual:\n"
            f"- Saldo disponible: ${saldo:,.2f}\n"
            f"- Suscripciones activas: {suscripciones}\n"
            f"- Gasto esencial: {'Sí' if esencial else 'No'}\n"
            f"- Nuevo gasto propuesto: ${nuevo_gasto:,.2f}\n"
            f"{contexto_historial}"
        )

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asesor financiero personal. Responde en español de forma cercana y personalizada."
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=280,
        )
        return resp.choices[0].message.content.strip()

    except Exception as e:
        return _generar_mensaje_fallback(
            saldo=saldo,
            suscripciones=suscripciones,
            esencial=esencial,
            nuevo_gasto=nuevo_gasto,
            historial_pagos=historial_pagos
        )


def _generar_mensaje_fallback(
    *,
    saldo: float,
    suscripciones: int,
    esencial: bool,
    nuevo_gasto: float,
    historial_pagos: list[dict] = None
) -> str:
    """Genera un mensaje personalizado sin usar GPT"""
    porcentaje = (nuevo_gasto / saldo * 100) if saldo > 0 else 100

    # Análisis del historial
    if historial_pagos and len(historial_pagos) > 0:
        montos = [p.get("monto", 0) for p in historial_pagos]
        promedio = sum(montos) / len(montos)
        total_pagos = len(historial_pagos)

        if nuevo_gasto > promedio * 1.5:
            patron = f"Este gasto (${nuevo_gasto:,.2f}) es significativamente mayor a tu promedio habitual (${promedio:,.2f}). "
        elif total_pagos >= 5:
            patron = f"Basándome en tus últimos {total_pagos} pagos, "
        else:
            patron = "Estoy aprendiendo tus hábitos de gasto. "
    else:
        patron = "Este es uno de tus primeros gastos. "

    tipo = "esencial" if esencial else "no esencial"

    mensaje = (
        f"⚠️ Alerta de gasto\n\n"
        f"{patron}"
        f"Este gasto {tipo} representa el {porcentaje:.1f}% de tu saldo actual.\n\n"
        f"Recomendaciones:\n"
    )

    if porcentaje > 40:
        mensaje += "1. Considera reducir el monto o buscar alternativas más económicas\n"
    if suscripciones > 5:
        mensaje += f"2. Tienes {suscripciones} suscripciones activas. Revisa cuáles realmente usas\n"
    if not esencial:
        mensaje += "3. Este gasto no es esencial. ¿Puedes posponerlo?\n"
    else:
        mensaje += "3. Si es esencial, busca la opción más económica disponible\n"

    return mensaje
