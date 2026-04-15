from app import db
import sqlalchemy.orm as so
from sqlalchemy.orm import relationship
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from datetime import date, datetime, timezone

#----------------------------------------------------------------------#

class User(db.Model):
    __tablename__ = "users"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(unique=True, nullable=False, index=True)
    password: so.Mapped[str] = so.mapped_column(nullable=False, index=True)
    role: so.Mapped[str] = so.mapped_column(nullable=False, index=True)

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

#----------------------------------------------------------------------#

class HealthLog(db.Model):
    __tablename__ = "health_logs"

    # foreign key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    patient_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("patient_profiles.id"),
        nullable=False)

    temperature: so.Mapped[float]
    bp_systolic: so.Mapped[int]
    bp_diastolic: so.Mapped[int]
    mood: so.Mapped[str]
    notes: so.Mapped[str]
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime,
        default=datetime.utcnow)

    # relationships
    patient = relationship("PatientProfile", back_populates="health_logs")

#----------------------------------------------------------------------#

class Checkup(db.Model):
    __tablename__ = "checkups"
    checkup_id: so.Mapped[int] = so.mapped_column(primary_key=True, nullable=False, index=True)

    patient_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("patient_profiles.id"),nullable=False)
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