# app.py
from flask import Flask, request, jsonify
from datetime import date
from dotenv import load_dotenv
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db
from models.user import User
from models.pago import Pago
from models.historial import Historial
from models.dinero import Dinero
from ml.model import evaluar_gasto
from ml.gpt import generar_mensaje_gpt
import os
import pymysql
from config import MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, MYSQL_DB

load_dotenv()

# Crear la base si no existe
conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS)
cursor = conn.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
cursor.close()
conn.close()

# --- Configuración base ---
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
db.init_app(app)

# --- Inicialización de la base y datos iniciales ---
with app.app_context():
    db.create_all()
    if not User.query.first():
        usuario = User(
            nombre="Carlos",
            apellido="Ramírez",
            correo="carlos@example.com",
            contrasena="1234",
            biometricos="bio1",
            numeroTelefono="5551234567"
        )
        db.session.add(usuario)
        db.session.flush()  # obtener idUser
        saldo = Dinero(saldo=4200.00, idUser=usuario.idUser)
        db.session.add(saldo)
        db.session.commit()

# --- Endpoint raíz ---
@app.get("/")
def ok():
    return jsonify({"ok": True})

# --- Endpoint de evaluación de gasto (IA) ---
@app.post("/api/evaluar")
def evaluar():
    data = request.get_json(force=True)
    user_id = data.get("idUser")

    historial_pagos = []
    if user_id:
        pagos = Pago.query.filter_by(idUser=user_id).order_by(Pago.pagoFecha).all()
        historial_pagos = [
            {
                "monto": float(p.monto),
                "motivo": p.motivo,
                "fecha": p.pagoFecha.isoformat() if p.pagoFecha else None
            }
            for p in pagos
        ]

    riesgo = evaluar_gasto(
        saldo=data["saldo"],
        suscripciones=data["suscripciones"],
        esencial=data["esencial"],
        nuevo_gasto=data["nuevo_gasto"],
        historial_pagos=historial_pagos,
    )

    if riesgo == 1:
        mensaje = generar_mensaje_gpt(
            saldo=data["saldo"],
            suscripciones=data["suscripciones"],
            esencial=data["esencial"],
            nuevo_gasto=data["nuevo_gasto"],
            historial_pagos=historial_pagos,
        )
        return jsonify({"alerta": True, "mensaje": mensaje})

    return jsonify({"alerta": False})

# --- Endpoint para registrar un pago ---
@app.post("/api/pago")
def registrar_pago():
    data = request.get_json(force=True)
    user_id = data.get("idUser")
    motivo = data.get("motivo")
    monto = data.get("monto")

    if not user_id or not motivo or monto is None:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    if monto <= 0:
        return jsonify({"error": "Monto inválido"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    dinero = Dinero.query.filter_by(idUser=user_id).first()
    if not dinero:
        return jsonify({"error": "No hay saldo asociado al usuario"}), 404
    if dinero.saldo < monto:
        return jsonify({"error": "Saldo insuficiente"}), 400

    # Crear el pago
    pago = Pago(idUser=user_id, motivo=motivo, pagoFecha=date.today(), monto=monto)
    db.session.add(pago)
    db.session.flush()  # obtener idPago

    # Actualizar saldo
    dinero.saldo -= monto

    # Crear historial
    hist = Historial(idDinero=dinero.idDinero, idPago=pago.idPago)
    db.session.add(hist)
    db.session.commit()

    return jsonify({
        "mensaje": "Pago registrado con éxito",
        "nuevo_saldo": float(dinero.saldo),
        "pago_id": pago.idPago
    })

# --- Endpoint para consultar saldo ---
@app.get("/api/saldo/<int:user_id>")
def obtener_saldo(user_id: int):
    dinero = Dinero.query.filter_by(idUser=user_id).first()
    if not dinero:
        return jsonify({"error": "Usuario o saldo no encontrado"}), 404
    return jsonify({"idUser": user_id, "saldo": float(dinero.saldo)})

# --- Inicio del servidor ---
if __name__ == "__main__":
    app.run(debug=True)
