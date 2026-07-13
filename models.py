from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(200),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    assignments = db.relationship(
        "Assignment",
        backref="user",
        lazy=True
    )

    attendance_records = db.relationship(
        "Attendance",
        backref="user",
        lazy=True
    )


class Assignment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(100),
        nullable=False
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    due_date = db.Column(
        db.Date,
        nullable=False
    )

    priority = db.Column(
        db.String(20),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


class Attendance(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    attended_classes = db.Column(
        db.Integer,
        default=0
    )

    total_classes = db.Column(
        db.Integer,
        default=0
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    @property
    def attendance_percentage(self):

        if self.total_classes == 0:
            return 0

        return round(
            (self.attended_classes / self.total_classes) * 100
        )