# app.py
from flask import Flask, request, jsonify, session, send_from_directory
from datetime import date, timedelta
from dotenv import load_dotenv
from config import (
    SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS,
    MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, MYSQL_DB,
)
from models import db
from models.user import User
from models.pago import Pago
from models.historial import Historial
from models.dinero import Dinero
from ml.model import evaluar_gasto
from ml.gpt import generar_mensaje_gpt
from services.balance_service import BalanceService
from services.payment_service import PaymentService
from sqlalchemy import text
import os
import pymysql

load_dotenv()

# ---------------------------------------------------------------------
# Crear DB si no existe
# ---------------------------------------------------------------------
conn = pymysql.connect(
    host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS, port=int(MYSQL_PORT)
)
cursor = conn.cursor()
cursor.execute(
    f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` "
    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
)
cursor.close()
conn.close()

# ---------------------------------------------------------------------
# Flask + SQLAlchemy + Sesión
# ---------------------------------------------------------------------
app = Flask(__name__, static_folder="public", static_url_path="/")
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS

app.secret_key = os.getenv("SESSION_SECRET", "dev-secret")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = bool(int(os.getenv("SESSION_COOKIE_SECURE", "0")))

db.init_app(app)

# ---------------------------------------------------------------------
# Bootstrapping: tablas, migraciones, normalización de contraseñas y semilla
# ---------------------------------------------------------------------
with app.app_context():
    db.create_all()

    # === Migraciones básicas ya existentes ===
    pago_table   = Pago.__table__.name
    dinero_table = Dinero.__table__.name

    # pagos.tipo
    existe_tipo = db.session.execute(text("""
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :tbl AND COLUMN_NAME = 'tipo'
    """), {"db": MYSQL_DB, "tbl": pago_table}).scalar()
    if not existe_tipo:
        db.session.execute(text(f"""
            ALTER TABLE `{pago_table}` ADD COLUMN `tipo` VARCHAR(10) NOT NULL DEFAULT 'debito'
        """))

    # dinero.deuda_credito
    existe_deuda = db.session.execute(text("""
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :tbl AND COLUMN_NAME = 'deuda_credito'
    """), {"db": MYSQL_DB, "tbl": dinero_table}).scalar()
    if not existe_deuda:
        db.session.execute(text(f"""
            ALTER TABLE `{dinero_table}` ADD COLUMN `deuda_credito` DECIMAL(12,2) NOT NULL DEFAULT 0
        """))
    db.session.commit()

    # === Migraciones mejoradas ===
    def col_exists(table: str, col: str) -> bool:
        return bool(db.session.execute(text("""
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :tbl AND COLUMN_NAME = :col LIMIT 1
        """), {"db": MYSQL_DB, "tbl": table, "col": col}).first())

    users_tbl = User.__table__.name
    pagos_tbl = Pago.__table__.name
    dinero_tbl = Dinero.__table__.name
    hist_tbl = Historial.__table__.name

    # users: created/updated y last_login_at
    if not col_exists(users_tbl, "created_at"):
        db.session.execute(text(f"ALTER TABLE `{users_tbl}` ADD COLUMN `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"))
    if not col_exists(users_tbl, "updated_at"):
        db.session.execute(text(f"ALTER TABLE `{users_tbl}` ADD COLUMN `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    if not col_exists(users_tbl, "last_login_at"):
        db.session.execute(text(f"ALTER TABLE `{users_tbl}` ADD COLUMN `last_login_at` DATETIME NULL"))

    # pagos: metadata + auditoría
    if not col_exists(pagos_tbl, "categoria"):
        db.session.execute(text(f"ALTER TABLE `{pagos_tbl}` ADD COLUMN `categoria` VARCHAR(60) NULL"))
    if not col_exists(pagos_tbl, "metodo"):
        db.session.execute(text(f"ALTER TABLE `{pagos_tbl}` ADD COLUMN `metodo` VARCHAR(20) NULL"))
    if not col_exists(pagos_tbl, "referencia"):
        db.session.execute(text(f"ALTER TABLE `{pagos_tbl}` ADD COLUMN `referencia` VARCHAR(80) NULL"))
    if not col_exists(pagos_tbl, "notas"):
        db.session.execute(text(f"ALTER TABLE `{pagos_tbl}` ADD COLUMN `notas` TEXT NULL"))
    if not col_exists(pagos_tbl, "created_at"):
        db.session.execute(text(f"ALTER TABLE `{pagos_tbl}` ADD COLUMN `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"))
    if not col_exists(pagos_tbl, "updated_at"):
        db.session.execute(text(f"ALTER TABLE `{pagos_tbl}` ADD COLUMN `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    # índice (si MySQL < 8.* ignora si falla)
    try:
        db.session.execute(text(f"CREATE INDEX IF NOT EXISTS idx_pagos_user_fecha ON `{pagos_tbl}` (idUser, pagoFecha)"))
    except Exception:
        pass

    # dinero: moneda + auditoría
    if not col_exists(dinero_tbl, "moneda"):
        db.session.execute(text(f"ALTER TABLE `{dinero_tbl}` ADD COLUMN `moneda` VARCHAR(3) NOT NULL DEFAULT 'MXN'"))
    if not col_exists(dinero_tbl, "created_at"):
        db.session.execute(text(f"ALTER TABLE `{dinero_tbl}` ADD COLUMN `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"))
    if not col_exists(dinero_tbl, "updated_at"):
        db.session.execute(text(f"ALTER TABLE `{dinero_tbl}` ADD COLUMN `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    # historial: auditoría
    if not col_exists(hist_tbl, "created_at"):
        db.session.execute(text(f"ALTER TABLE `{hist_tbl}` ADD COLUMN `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"))
    db.session.commit()

    # --- Normaliza contraseñas antiguas (plano -> hash) ---
    from werkzeug.security import generate_password_hash
    def _es_hash(c: str) -> bool:
        return isinstance(c, str) and c.startswith("pbkdf2:sha256:")
    users = User.query.all()
    changed = 0
    for u in users:
        if not _es_hash(u.contrasena) and u.contrasena:
            u.contrasena = generate_password_hash(u.contrasena, method="pbkdf2:sha256", salt_length=16)
            changed += 1
    if changed:
        db.session.commit()
        print(f"[migracion] Contraseñas convertidas a hash: {changed}")

    # --- Semilla mínima (si DB vacía) ---
    if not User.query.first():
        usuario = User(
            nombre="Carlos",
            apellido="Ramírez",
            correo="carlos@example.com",
            contrasena="",
            biometricos="bio1",
            numeroTelefono="5551234567",
        )
        usuario.set_password("1234")
        db.session.add(usuario)
        db.session.flush()

        saldo = Dinero(saldo=4200.00, deuda_credito=1200.00, idUser=usuario.idUser)
        db.session.add(saldo)

        p1 = Pago(idUser=usuario.idUser, motivo="Netflix",    pagoFecha=date.today(), monto=250.00,  tipo="credito", categoria="entretenimiento")
        p2 = Pago(idUser=usuario.idUser, motivo="Super",      pagoFecha=date.today(), monto=800.00,  tipo="debito",  categoria="hogar")
        p3 = Pago(idUser=usuario.idUser, motivo="Transporte", pagoFecha=date.today(), monto=120.50,  tipo="debito",  categoria="movilidad")
        db.session.add_all([p1, p2, p3]); db.session.flush()
        for p in (p1, p2, p3):
            db.session.add(Historial(idDinero=saldo.idDinero, idPago=p.idPago))
        db.session.commit()

    # --- Verificar usuarios sin saldo y crearles uno ---
    users_sin_saldo = db.session.query(User).outerjoin(Dinero).filter(Dinero.idDinero == None).all()
    if users_sin_saldo:
        for u in users_sin_saldo:
            nuevo_saldo = Dinero(saldo=0, deuda_credito=0, idUser=u.idUser)
            db.session.add(nuevo_saldo)
        db.session.commit()
        print(f"[migracion] Se creó saldo para {len(users_sin_saldo)} usuario(s) sin registro de saldo")

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)

def require_auth_user():
    user = current_user()
    if not user:
        return None, (jsonify({"error": "unauthorized"}), 401)
    return user, None

# ---------------------------------------------------------------------
# Rutas estáticas
# ---------------------------------------------------------------------
@app.get("/")
def root_index():
    return send_from_directory(app.static_folder, "index.html")

@app.get("/dashboard.html")
def dash_html():
    return send_from_directory(app.static_folder, "dashboard.html")

@app.get("/health")
def ok():
    return jsonify({"ok": True})

# ---------------------------------------------------------------------
# Auth (hash + last_login_at)
# ---------------------------------------------------------------------
@app.post("/api/login")
def login():
    data = request.get_json(force=True)
    correo = (data.get("correo") or "").strip()
    contrasena = (data.get("contrasena") or "").strip()
    remember = bool(data.get("remember", False))

    if not correo or not contrasena:
        return jsonify({"error": "Faltan datos"}), 400

    user = User.query.filter_by(correo=correo).first()
    if not user or not user.check_password(contrasena):
        return jsonify({"error": "Usuario o contraseña inválidos"}), 401

    session["user_id"] = user.idUser
    session.permanent = remember

    from sqlalchemy.sql import func as _func
    user.last_login_at = db.session.execute(db.select(_func.now())).scalar_one()
    db.session.commit()

    return jsonify({"ok": True, "user": {
        "idUser": user.idUser, "nombre": user.nombre, "apellido": user.apellido, "correo": user.correo
    }})

@app.post("/api/register")
def register():
    """
    Registra un nuevo usuario en el sistema.
    Body: {
        "nombre": str,
        "apellido": str,
        "correo": str (email único),
        "contrasena": str,
        "numeroTelefono": str (opcional),
        "biometricos": str (opcional),
        "saldo_inicial": float (opcional, default 0)
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Falta el cuerpo de la petición"}), 400

    # Validaciones básicas
    nombre = (data.get("nombre") or "").strip()
    apellido = (data.get("apellido") or "").strip()
    correo = (data.get("correo") or "").strip().lower()
    contrasena = (data.get("contrasena") or "").strip()
    numeroTelefono = (data.get("numeroTelefono") or "").strip()
    biometricos = (data.get("biometricos") or "").strip()
    saldo_inicial = float(data.get("saldo_inicial", 0))

    if not nombre:
        return jsonify({"error": "El nombre es requerido"}), 400
    if not apellido:
        return jsonify({"error": "El apellido es requerido"}), 400
    if not correo:
        return jsonify({"error": "El correo es requerido"}), 400
    if not contrasena:
        return jsonify({"error": "La contraseña es requerida"}), 400
    if len(contrasena) < 4:
        return jsonify({"error": "La contraseña debe tener al menos 4 caracteres"}), 400

    # Validar formato de correo (básico)
    if "@" not in correo or "." not in correo.split("@")[1]:
        return jsonify({"error": "Formato de correo inválido"}), 400

    # Verificar que el correo no exista
    existing_user = User.query.filter_by(correo=correo).first()
    if existing_user:
        return jsonify({"error": "El correo ya está registrado"}), 409

    try:
        # Crear usuario
        nuevo_usuario = User(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            contrasena="",  # Se establece con set_password
            numeroTelefono=numeroTelefono or None,
            biometricos=biometricos or None
        )
        nuevo_usuario.set_password(contrasena)
        db.session.add(nuevo_usuario)
        db.session.flush()

        # Crear saldo inicial
        dinero = BalanceService.create_balance(nuevo_usuario.idUser, saldo_inicial)
        db.session.commit()

        return jsonify({
            "mensaje": "Usuario registrado exitosamente",
            "usuario": {
                "idUser": nuevo_usuario.idUser,
                "nombre": nuevo_usuario.nombre,
                "apellido": nuevo_usuario.apellido,
                "correo": nuevo_usuario.correo,
                "saldo_inicial": float(dinero.saldo)
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al registrar usuario", "detail": str(e)}), 500

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.get("/api/me")
def me():
    user = current_user()
    if not user:
        return jsonify({"user": None})
    return jsonify({"user": {
        "idUser": user.idUser, "nombre": user.nombre, "apellido": user.apellido, "correo": user.correo
    }})

# ---------------------------------------------------------------------
# Evaluación de gasto (ML)
# ---------------------------------------------------------------------
@app.post("/api/evaluar")
def evaluar():
    data = request.get_json(force=True)

    # usar sesión si no llega idUser
    user_id = data.get("idUser")
    if not user_id:
        user, err = require_auth_user()
        if err: return err
        user_id = user.idUser

    pagos = Pago.query.filter_by(idUser=user_id).order_by(Pago.pagoFecha).all()
    historial_pagos = [{
        "monto": float(p.monto),
        "motivo": p.motivo,
        "fecha": p.pagoFecha.isoformat() if p.pagoFecha else None,
    } for p in pagos]

    try:
        riesgo = evaluar_gasto(
            saldo=float(data["saldo"]),
            suscripciones=int(data.get("suscripciones", 0)),
            esencial=int(data.get("esencial", 1)),
            nuevo_gasto=float(data["nuevo_gasto"]),
            historial_pagos=historial_pagos,
        )
    except KeyError:
        return jsonify({"error": "Payload incompleto"}), 400

    if riesgo == 1:
        mensaje = generar_mensaje_gpt(
            saldo=float(data["saldo"]),
            suscripciones=int(data.get("suscripciones", 0)),
            esencial=int(data.get("esencial", 1)),
            nuevo_gasto=float(data["nuevo_gasto"]),
            historial_pagos=historial_pagos,
        )
        return jsonify({"alerta": True, "mensaje": mensaje})
    return jsonify({"alerta": False})

# ---------------------------------------------------------------------
# Registrar pago (con metadata)
# ---------------------------------------------------------------------
@app.post("/api/pago")
def registrar_pago():
    data = request.get_json(force=True)
    user, err = require_auth_user()
    if err:
        return err

    motivo = (data.get("motivo") or "").strip()
    tipo = (data.get("tipo") or "debito").strip().lower()
    monto = data.get("monto")
    categoria = data.get("categoria") or None
    metodo = data.get("metodo") or None
    referencia = data.get("referencia") or None
    notas = data.get("notas") or None

    try:
        monto = float(monto)
    except (TypeError, ValueError):
        return jsonify({"error": "Monto inválido"}), 400

    try:
        result = PaymentService.register_payment(
            user.idUser, motivo, monto, tipo,
            categoria, metodo, referencia, notas
        )
        db.session.commit()

        return jsonify({
            "mensaje": "Movimiento registrado",
            **result
        })
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al registrar pago", "detail": str(e)}), 500

@app.post("/api/pagar_tarjeta")
def pagar_tarjeta():
    user, err = require_auth_user()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    raw = data.get("monto", None)
    try:
        monto = float(raw)
    except (TypeError, ValueError):
        return jsonify({"error": "Monto inválido o no enviado"}), 400

    try:
        result = PaymentService.pay_credit_card(user.idUser, monto)
        db.session.commit()
        return jsonify(result)
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al pagar tarjeta", "detail": str(e)}), 500

# ---------------------------------------------------------------------
# Saldo actual (usado por el front)
# ---------------------------------------------------------------------
@app.get("/api/saldo")
def obtener_saldo_sesion():
    user, err = require_auth_user()
    if err:
        return err
    try:
        balance_info = BalanceService.get_balance_info(user.idUser)
        return jsonify(balance_info)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

# ---------------------------------------------------------------------
# Dashboard + Movimientos (paginado)
# ---------------------------------------------------------------------
@app.get("/api/dashboard")
def obtener_dashboard_sesion():
    user, err = require_auth_user()
    if err:
        return err
    return _dashboard_payload(user.idUser)

@app.get("/api/dashboard/<int:user_id>")
def obtener_dashboard(user_id: int):
    return _dashboard_payload(user_id)

def _dashboard_payload(user_id: int):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    dinero = Dinero.query.filter_by(idUser=user_id).first()
    if not dinero:
        return jsonify({"error": "No se encontró saldo asociado"}), 404

    res = (
        db.session.query(Historial, Pago)
        .join(Pago, Historial.idPago == Pago.idPago)
        .filter(Historial.idDinero == dinero.idDinero)
        .order_by(Pago.pagoFecha.desc(), Pago.idPago.desc())
        .limit(10).all()
    )
    movimientos = [{
        "motivo": p.motivo,
        "monto": float(p.monto),
        "signo": "-" if (p.tipo or "debito") == "debito" else "+",
        "fecha": p.pagoFecha.isoformat() if p.pagoFecha else None,
        "tipo": p.tipo or "debito",
        "categoria": getattr(p, "categoria", None),
        "metodo": getattr(p, "metodo", None),
    } for _, p in res]

    moneda = getattr(dinero, "moneda", None) or "MXN"

    return jsonify({
        "usuario": f"{user.nombre} {user.apellido}".strip(),
        "saldo": float(dinero.saldo),
        "deuda_credito": float(getattr(dinero, "deuda_credito", 0) or 0),
        "moneda": moneda,
        "movimientos": movimientos
    })

@app.get("/api/movimientos")
def movimientos_sesion():
    user, err = require_auth_user()
    if err:
        return err

    try:
        page = max(int(request.args.get("page", "1")), 1)
        per_page = min(max(int(request.args.get("per_page", "10")), 1), 50)
        tipo = (request.args.get("tipo", "") or "").strip().lower()
    except ValueError:
        return jsonify({"error": "Parámetros inválidos"}), 400

    dinero = BalanceService.get_balance_by_user(user.idUser)
    if not dinero:
        return jsonify({"error": "No se encontró saldo asociado"}), 404

    result = PaymentService.get_payments_by_user(
        user.idUser, dinero.idDinero, page, per_page, tipo if tipo else None
    )
    return jsonify(result)

@app.post("/api/transferir")
def transferir():
    user, err = require_auth_user()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    clabe = (data.get("clabe") or "").strip()
    monto_raw = data.get("monto")
    concepto = (data.get("concepto") or "Transferencia").strip()

    if not clabe:
        return jsonify({"error": "CLABE es requerida"}), 400
    if len(clabe) != 18 or not clabe.isdigit():
        return jsonify({"error": "CLABE debe tener 18 dígitos"}), 400

    try:
        monto = float(monto_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "Monto inválido"}), 400

    if monto <= 0:
        return jsonify({"error": "Monto debe ser mayor a 0"}), 400

    try:
        result = PaymentService.register_payment(
            user.idUser,
            f"Transferencia: {concepto}",
            monto,
            "debito",
            categoria="transferencia",
            metodo="spei",
            referencia=clabe
        )
        db.session.commit()

        return jsonify({
            "mensaje": "Transferencia exitosa",
            "clabe_destino": clabe,
            "monto": monto,
            "concepto": concepto,
            **result
        })
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al realizar transferencia", "detail": str(e)}), 500

# ----- Errores en JSON (para que el front no reciba HTML) -----
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError

@app.errorhandler(Exception)
def handle_any_error(e):
    if isinstance(e, HTTPException):
        return jsonify({"error": e.description, "status": e.code}), e.code
    # Excepciones de base de datos
    if isinstance(e, (IntegrityError, OperationalError)):
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({"error": str(e.__class__.__name__), "detail": str(e)}), 500
    # Resto
    return jsonify({"error": "internal_error", "detail": str(e)}), 500


# ---------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
