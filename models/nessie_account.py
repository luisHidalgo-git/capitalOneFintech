from __future__ import annotations
from . import db

class NessieAccount(db.Model):
    __tablename__ = "nessie_accounts"

    id = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey("users.idUser"), nullable=False, index=True)
    nessie_customer_id = db.Column(db.String(100), nullable=True)
    nessie_account_id = db.Column(db.String(100), nullable=True)
    account_type = db.Column(db.String(50), nullable=True)
    nickname = db.Column(db.String(100), nullable=True)

    user = db.relationship("User", backref="nessie_accounts")

    def __repr__(self):
        return f"<NessieAccount {self.id} customer={self.nessie_customer_id}>"
