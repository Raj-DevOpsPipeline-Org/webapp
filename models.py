import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UUID, CheckConstraint

db = SQLAlchemy()


class Account(db.Model):
    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    )
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    account_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    account_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # create relation with other tables
    assignments = db.relationship("Assignment", backref="account", lazy=True)


class Assignment(db.Model):
    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    )
    name = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer)
    num_of_attempts = db.Column(db.Integer)
    deadline = db.Column(db.DateTime, nullable=False)
    assignment_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    assignment_updated = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    account_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("account.id"), nullable=False
    )

    __table_args__ = (
        CheckConstraint("points>=1 AND points<=100", name="check_points"),
        CheckConstraint(
            "num_of_attempts>=1 AND num_of_attempts<=10", name="check_num_of_attempts"
        ),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "points": self.points,
            "num_of_attempts": self.num_of_attempts,
            "deadline": self.deadline.isoformat(),
            "assignment_created": self.assignment_created.isoformat(),
            "assignment_updated": self.assignment_updated.isoformat(),
        }

class AssignmentSubmission(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    assignment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assignment.id'), nullable=False)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'), nullable=False)
    submission_url = db.Column(db.String(255), nullable=False)
    submission_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    submission_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account = db.relationship("Account", backref="submissions")
    assignment = db.relationship("Assignment", backref="submissions")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "assignment_id": str(self.assignment_id),
            "submission_url": self.submission_url,
            "submission_date": self.submission_date.isoformat(),
            "submission_updated": self.submission_updated.isoformat()
        }
        
# To have original submission timstamp and modified updated tiemstamp

# class AssignmentSubmission(db.Model):
#     id = db.Column(
#         UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
#     )
#     assignment_id = db.Column(
#         UUID(as_uuid=True), db.ForeignKey("assignment.id"), nullable=False
#     )
#     account_id = db.Column(
#         UUID(as_uuid=True), db.ForeignKey("account.id"), nullable=False
#     )
#     submission_url = db.Column(db.String(255), nullable=False)
#     submission_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     submission_updated = db.Column(
#         db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
#     )
#     attempts = db.Column(db.Integer, default=1)

#     account = db.relationship("Account", backref="submissions")
#     assignment = db.relationship("Assignment", backref="submissions")

#     def to_dict(self):
#         return {
#             "id": str(self.id),
#             "assignment_id": str(self.assignment_id),
#             "submission_url": self.submission_url,
#             "submission_date": self.submission_date.isoformat(),
#             "submission_updated": self.submission_updated.isoformat(),
#         }
