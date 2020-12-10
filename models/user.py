from db import db
from flask import request, url_for
from requests import Response, post

MAILGUN_DOMAIN = "sandboxaf5bd86dcdf3432fa1da7b1cbe4b4096.mailgun.org"
MAILGUN_API_KEY = "99b76806e5b8fff001e40b4197ed66c9-4879ff27-b8c51d14"
FROM_TITLE = "Stores REST API"
FROM_EMAIL = "https://api.mailgun.net/v3/sandboxaf5bd86dcdf3432fa1da7b1cbe4b4096.mailgun.org"


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False,)
    email = db.Column(db.String(80), nullable=False, unique=True)
    activated = db.Column(db.Boolean, default=False)
    stores = db.relationship("StoreModel", lazy="dynamic")

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first() 

    def send_confirmation_email(self):
        # http://127.0.0.1:5000/
        link = request.url_root[0:-1] + url_for("userconfirm", user_id=self.id)

        return post(
            f"http://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"{FROM_TITLE} <{FROM_EMAIL}>",
                "to": self.email,
                "subject": "Registration confirmation",
                "text": f"Please click the link to confirm your registration: {link}"
            },
        )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
