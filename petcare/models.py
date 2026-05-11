from enum import Enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


class TimestampMixin:
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class SpeciesDBEnum(str, Enum):
    dog = "dog"
    cat = "cat"
    other = "other"


class SexDBEnum(str, Enum):
    male = "male"
    female = "female"
    unknown = "unknown"


class ScheduleEventTypeDBEnum(str, Enum):
    vaccine = "vaccine"
    grooming = "grooming"
    checkup = "checkup"
    medication = "medication"
    walk = "walk"
    other = "other"


class VisitTypeDBEnum(str, Enum):
    checkup = "checkup"
    consultation = "consultation"
    vaccination = "vaccination"
    surgery = "surgery"
    emergency = "emergency"
    other = "other"


class SeverityDBEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    emergency = "emergency"


species_enum = SAEnum(
    SpeciesDBEnum,
    name="species_enum",
    native_enum=False,
    validate_strings=True,
)
sex_enum = SAEnum(
    SexDBEnum,
    name="sex_enum",
    native_enum=False,
    validate_strings=True,
)
event_type_enum = SAEnum(
    ScheduleEventTypeDBEnum,
    name="schedule_event_type_enum",
    native_enum=False,
    validate_strings=True,
)
visit_type_enum = SAEnum(
    VisitTypeDBEnum,
    name="visit_type_enum",
    native_enum=False,
    validate_strings=True,
)
severity_enum = SAEnum(
    SeverityDBEnum,
    name="severity_enum",
    native_enum=False,
    validate_strings=True,
)


class Owner(TimestampMixin, Base):
    __tablename__ = "owners"
    __table_args__ = (
        Index("ix_owners_name", "name"),
        Index("ix_owners_phone", "phone"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(30), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(String(200), nullable=True)
    notes = Column(String(500), nullable=True)

    pets = relationship("Pet", back_populates="owner")


class Hospital(TimestampMixin, Base):
    __tablename__ = "hospitals"
    __table_args__ = (
        Index("ix_hospitals_name", "name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(30), nullable=True)
    address = Column(String(200), nullable=True)
    notes = Column(String(500), nullable=True)

    health_records = relationship("HealthRecord", back_populates="hospital")


class Pet(TimestampMixin, Base):
    __tablename__ = "pets"
    __table_args__ = (
        CheckConstraint("weight > 0", name="ck_pets_weight_positive"),
        Index("ix_pets_owner_name", "owner_name"),
        Index("ix_pets_owner_id", "owner_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    species = Column(species_enum, nullable=False, index=True)
    breed = Column(String(50), nullable=True)
    sex = Column(sex_enum, nullable=True)
    birth_date = Column(Date, nullable=False)
    weight = Column(Float, nullable=False)
    sterilized = Column(Boolean, nullable=False, default=False)
    owner_id = Column(Integer, ForeignKey("owners.id", ondelete="SET NULL"), nullable=True)
    owner_name = Column(String(50), nullable=False)
    special_notes = Column(String(500), nullable=True)

    owner = relationship("Owner", back_populates="pets")
    health_records = relationship(
        "HealthRecord", back_populates="pet", cascade="all, delete-orphan"
    )
    vaccinations = relationship(
        "Vaccination", back_populates="pet", cascade="all, delete-orphan"
    )
    schedules = relationship(
        "Schedule", back_populates="pet", cascade="all, delete-orphan"
    )


class HealthRecord(TimestampMixin, Base):
    __tablename__ = "health_records"
    __table_args__ = (
        CheckConstraint("cost >= 0", name="ck_health_records_cost_non_negative"),
        Index("ix_health_records_pet_record_date", "pet_id", "record_date"),
        Index("ix_health_records_hospital_id", "hospital_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True)
    record_date = Column(Date, nullable=False)
    symptom = Column(String(200), nullable=False)
    treatment = Column(String(200), nullable=False)
    diagnosis = Column(String(200), nullable=True)
    prescription = Column(String(200), nullable=True)
    veterinarian_name = Column(String(100), nullable=True)
    visit_type = Column(visit_type_enum, nullable=True, index=True)
    severity = Column(severity_enum, nullable=True, index=True)
    cost = Column(Float, nullable=False)

    pet = relationship("Pet", back_populates="health_records")
    hospital = relationship("Hospital", back_populates="health_records")


class Vaccination(TimestampMixin, Base):
    __tablename__ = "vaccinations"
    __table_args__ = (
        CheckConstraint("cost >= 0", name="ck_vaccinations_cost_non_negative"),
        CheckConstraint(
            "next_due_date >= vaccination_date",
            name="ck_vaccinations_due_after_vaccination",
        ),
        Index("ix_vaccinations_pet_next_due_date", "pet_id", "next_due_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    vaccine_name = Column(String(100), nullable=False)
    vaccination_date = Column(Date, nullable=False)
    next_due_date = Column(Date, nullable=False)
    cost = Column(Float, nullable=False)

    pet = relationship("Pet", back_populates="vaccinations")


class Schedule(TimestampMixin, Base):
    __tablename__ = "schedules"
    __table_args__ = (
        Index("ix_schedules_pet_schedule_date", "pet_id", "schedule_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(event_type_enum, nullable=False, index=True)
    description = Column(String(200), nullable=False)
    schedule_date = Column(Date, nullable=False)

    pet = relationship("Pet", back_populates="schedules")
