from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="employee")  # 'admin' | 'employee'
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    entries = db.relationship(
        "TimeEntry", backref="user", lazy="dynamic",
        foreign_keys="TimeEntry.user_id", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    entries = db.relationship("TimeEntry", backref="project", lazy="dynamic")

    def __repr__(self):
        return f"<Project {self.name}>"


class TimeEntry(db.Model):
    """
    Una singola riga di pianificazione/rendicontazione:
    un dipendente, in una data, su un progetto, per N ore.
    """
    __tablename__ = "time_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)

    work_date = db.Column(db.Date, nullable=False, index=True)
    hours = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String(255), nullable=True)

    # 'pianificato' = inserito dal dipendente, non ancora bloccato
    # 'confermato' = validato dall'admin, pronto per la busta paga
    status = db.Column(db.String(20), nullable=False, default="pianificato")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "project_id", "work_date", name="uq_user_project_date"),
    )

    def __repr__(self):
        return f"<TimeEntry user={self.user_id} project={self.project_id} date={self.work_date} h={self.hours}>"
