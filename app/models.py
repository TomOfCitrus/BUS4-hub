from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy.orm as so
from sqlalchemy.orm import relationship, Mapped, mapped_column
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from datetime import date, datetime, timezone
import secrets

#----------------------------------------------------------------------#

class User(db.Model):
    __tablename__ = "users"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    first_name: so.Mapped[str] = so.mapped_column(nullable=False, index=True)
    last_name: so.Mapped[str] = so.mapped_column(nullable=False, index=True)
    date_of_birth: so.Mapped[datetime] = so.mapped_column(sa.DATE, nullable=False, index=True)
    email: so.Mapped[str] = so.mapped_column(unique=True, nullable=False, index=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    role: so.Mapped[str] = so.mapped_column(nullable=False, index=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#----------------------------------------------------------------------#

class PatientProfile(db.Model):
    __tablename__ = "patient_profiles"

    # foreign key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("users.id"),
        nullable=False,
        unique=True)

    first_name: so.Mapped[str] = so.mapped_column(nullable=False, index=True)
    last_name: so.Mapped[str] = so.mapped_column(nullable=False, index=True)
    date_of_birth: so.Mapped[date] = so.mapped_column(sa.DATE, nullable=False)

    # primary health record
    hypertension: so.Mapped[bool] = so.mapped_column(default=False)
    diabetes: so.Mapped[bool] = so.mapped_column(default=False)
    heart_disease: so.Mapped[bool] = so.mapped_column(default=False)
    arthritis: so.Mapped[bool] = so.mapped_column(default=False)
    osteoporosis: so.Mapped[bool] = so.mapped_column(default=False)
    copd: so.Mapped[bool] = so.mapped_column(default=False)
    stroke: so.Mapped[bool] = so.mapped_column(default=False)
    dementia: so.Mapped[bool] = so.mapped_column(default=False)
    vision_problems: so.Mapped[bool] = so.mapped_column(default=False)
    hearing_loss: so.Mapped[bool] = so.mapped_column(default=False)
    allergies: so.Mapped[str] = so.mapped_column(default="")
    smoking_status: so.Mapped[str] = so.mapped_column(default="")
    alcohol_consumption: so.Mapped[str] = so.mapped_column(default="")
    physical_activity: so.Mapped[str] = so.mapped_column(default="")

    # relationships
    user = relationship("User")
    health_logs = relationship("HealthLog", back_populates="patient")
    checkups = relationship("Checkup", back_populates="patient")
    approved_relatives = relationship("RelativeApproval", back_populates="patient", foreign_keys="RelativeApproval.patient_id")

#----------------------------------------------------------------------#

class HealthLog(db.Model):
    __tablename__ = "health_logs"

    # foreign key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    patient_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("patient_profiles.user_id"),
        nullable=False)

    temperature: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False, index=True)
    bp_systolic: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False, index=True)
    bp_diastolic: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False, index=True)
    mood: so.Mapped[str] = so.mapped_column(sa.String, nullable=False, index=True)
    notes: so.Mapped[str] = so.mapped_column(sa.String(500))
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime,
        default=datetime.utcnow)

    # relationships
    patient = relationship("PatientProfile", back_populates="health_logs")

#----------------------------------------------------------------------#

class Checkup(db.Model):
    __tablename__ = "checkups"
    checkup_id: so.Mapped[int] = so.mapped_column(primary_key=True, nullable=False, index=True)

    patient_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("patient_profiles.user_id"),nullable=False)
    patient_last_name: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False, index=True)
    patient_first_name: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False, index=True)

    gp_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)

    checkup_date: so.Mapped[datetime] = so.mapped_column(sa.DATE, nullable=False, default=lambda: datetime.now(timezone.utc))
    medication: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False, index=True)
    dosage: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False, index=True)
    notes: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False, index=True)

    #relationships
    patient = relationship("PatientProfile", back_populates="checkups")
    gp = relationship("User")

    def __repr__(self):
        return (f'<Checkup {self.checkup_id}, {self.patient_last_name}, {self.patient_first_name}, '
                f'{self.checkup_date}, {self.medication}, {self.dosage}, {self.notes}>')

#----------------------------------------------------------------------#

class RelativeApproval(db.Model):
    __tablename__ = "relative_approvals"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    patient_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("patient_profiles.user_id"),
        nullable=False,
        index=True)
    relative_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("users.id"),
        nullable=False,
        index=True)

    approved_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime,
        default=datetime.utcnow,
        nullable=False)

    # relationships
    patient = relationship("PatientProfile", back_populates="approved_relatives", foreign_keys=[patient_id])
    relative = relationship("User")

    def __repr__(self):
        return f'<RelativeApproval Patient: {self.patient_id}, Relative: {self.relative_id}>'

#----------------------------------------------------------------------#

class RelativeInvite(db.Model):
    __tablename__ = "relative_invites"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    patient_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("patient_profiles.user_id"),
        nullable=False,
        index=True)

    token: so.Mapped[str] = so.mapped_column(sa.String(128), unique=True, nullable=False, index=True)

    relative_email: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False, index=True)

    expires_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, nullable=False)
    used: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False, nullable=False)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    def generate_token(self):
        self.token = secrets.token_urlsafe(32)

    def is_valid(self):
        return (not self.used) and (self.expires_at > datetime.utcnow())