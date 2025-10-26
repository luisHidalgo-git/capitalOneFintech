# config.py
import os

MYSQL_USER = os.getenv("MYSQL_USER", "luis")
MYSQL_PASS = os.getenv("MYSQL_PASS", "dominic06")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB   = os.getenv("MYSQL_DB", "bancodigital")

if MYSQL_PASS:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )
else:
    # sin contraseña -> NO pongas ':'
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )

SQLALCHEMY_TRACK_MODIFICATIONS = False
