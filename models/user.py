# models/user.py
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func

class User(db.Model):
    __tablename__ = "users"
    idUser = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=True)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    # Guardamos HASH, no texto plano
    contrasena = db.Column(db.String(255), nullable=False)
    biometricos = db.Column(db.String(255), nullable=True)
    numeroTelefono = db.Column(db.String(30), nullable=True)

    # NUEVO: auditoría
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    last_login_at = db.Column(db.DateTime, nullable=True)

    pagos = db.relationship("Pago", backref="user", lazy=True)
    dinero = db.relationship("Dinero", backref="user", uselist=False, lazy=True)

    # Helpers de contraseña
    def set_password(self, plain: str) -> None:
        self.contrasena = generate_password_hash(
            plain, method="pbkdf2:sha256", salt_length=16
        )

    def check_password(self, plain: str) -> bool:
        return check_password_hash(self.contrasena, plain)
