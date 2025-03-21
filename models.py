from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    verification_code = db.Column(db.String(6))
    code_created_at = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_verification_code(self, code):
        self.verification_code = code
        self.code_created_at = datetime.datetime.utcnow()

    def check_verification_code(self, code):
        if not self.code_created_at:
            return False
        # 验证码10分钟内有效
        if (datetime.datetime.utcnow() - self.code_created_at).total_seconds() > 600:
            return False
        return self.verification_code == code
