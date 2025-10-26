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
            "Eres un asesor financiero personal y empático. Genera un mensaje de alerta que:\n"
            "1. En 1-2 líneas: Explica el riesgo principal de este gasto basándote en el saldo y patrones\n"
            "2. Agrega una sección 'Recomendaciones:' con 2-3 puntos concretos y accionables\n"
            "3. Usa un tono cercano pero profesional\n"
            "4. Sé conciso (máximo 200 palabras)\n"
            "5. Usa números y datos específicos del usuario\n\n"
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
    saldo_restante = saldo - nuevo_gasto

    # Análisis del historial
    patron = ""
    if historial_pagos and len(historial_pagos) > 0:
        montos = [p.get("monto", 0) for p in historial_pagos]
        promedio = sum(montos) / len(montos)
        total_pagos = len(historial_pagos)

        if nuevo_gasto > promedio * 1.5:
            patron = f"Este gasto de ${nuevo_gasto:,.2f} supera tu promedio habitual (${promedio:,.2f}). "
        elif total_pagos >= 5:
            patron = f"Analizando tus últimos {total_pagos} pagos, "
        else:
            patron = "Estoy aprendiendo sobre tus hábitos. "
    else:
        patron = "Este es tu primer gasto registrado. "

    tipo = "esencial" if esencial else "no esencial"

    mensaje = (
        f"{patron}"
        f"Este gasto {tipo} representa el <strong>{porcentaje:.1f}%</strong> de tu saldo. "
        f"Te quedarían ${saldo_restante:,.2f}.\n\n"
        f"<strong>Recomendaciones:</strong>\n"
    )

    recs = []
    if porcentaje > 50:
        recs.append("• Considera reducir el monto o dividirlo en varios pagos")
    elif porcentaje > 40:
        recs.append("• Busca alternativas más económicas para este gasto")

    if suscripciones > 5:
        recs.append(f"• Tienes {suscripciones} suscripciones activas. Revisa cuáles realmente usas")

    if not esencial:
        recs.append("• Este gasto no es esencial. ¿Puedes posponerlo hasta recibir más ingresos?")
    else:
        recs.append("• Si es esencial, compara precios entre diferentes proveedores")

    if porcentaje > 30:
        recs.append(f"• Considera mantener al menos ${saldo*0.3:,.2f} como fondo de emergencia")

    mensaje += "\n".join(recs[:3])  # Máximo 3 recomendaciones
    return mensaje
