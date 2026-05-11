from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Query, Session

import models
import schemas
from ml_health import predict_health_risk


DUE_SOON_DAYS = 30


def _paginate(query: Query, skip: int, limit: int):
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


def _apply_updates(instance, update_data: dict):
    for key, value in update_data.items():
        setattr(instance, key, value)


def _validate_vaccination_patch(existing: models.Vaccination, update_data: dict):
    merged = {
        "vaccine_name": update_data.get("vaccine_name", existing.vaccine_name),
        "vaccination_date": update_data.get("vaccination_date", existing.vaccination_date),
        "next_due_date": update_data.get("next_due_date", existing.next_due_date),
        "cost": update_data.get("cost", existing.cost),
    }
    schemas.VaccinationCreate.model_validate(merged)


def _get_owner_or_none(db: Session, owner_id: int | None):
    if owner_id is None:
        return None
    return db.query(models.Owner).filter(models.Owner.id == owner_id).first()


def _get_hospital_or_none(db: Session, hospital_id: int | None):
    if hospital_id is None:
        return None
    return db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()


# owner CRUD

def create_owner(db: Session, owner: schemas.OwnerCreate):
    db_owner = models.Owner(**owner.model_dump())
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)
    return db_owner


def get_owner(db: Session, owner_id: int):
    return db.query(models.Owner).filter(models.Owner.id == owner_id).first()


def get_owners_paginated(db: Session, skip: int = 0, limit: int = 20, keyword: str | None = None):
    query = db.query(models.Owner)
    if keyword:
        keyword = keyword.strip()
        query = query.filter(
            models.Owner.name.ilike(f"%{keyword}%")
            | models.Owner.phone.ilike(f"%{keyword}%")
            | models.Owner.email.ilike(f"%{keyword}%")
        )
    query = query.order_by(models.Owner.id.desc())
    return _paginate(query, skip, limit)


def update_owner(db: Session, owner_id: int, owner_update: schemas.OwnerUpdate):
    owner = get_owner(db, owner_id)
    if owner is None:
        return None

    update_data = owner_update.model_dump(exclude_unset=True)
    _apply_updates(owner, update_data)

    if "name" in update_data:
        db.query(models.Pet).filter(models.Pet.owner_id == owner.id).update(
            {models.Pet.owner_name: owner.name}, synchronize_session=False
        )

    db.commit()
    db.refresh(owner)
    return owner


def delete_owner(db: Session, owner_id: int):
    owner = get_owner(db, owner_id)
    if owner is None:
        return None

    db.query(models.Pet).filter(models.Pet.owner_id == owner.id).update(
        {models.Pet.owner_id: None}, synchronize_session=False
    )
    db.delete(owner)
    db.commit()
    return owner


# hospital CRUD

def create_hospital(db: Session, hospital: schemas.HospitalCreate):
    db_hospital = models.Hospital(**hospital.model_dump())
    db.add(db_hospital)
    db.commit()
    db.refresh(db_hospital)
    return db_hospital


def get_hospital(db: Session, hospital_id: int):
    return db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()


def get_hospitals_paginated(db: Session, skip: int = 0, limit: int = 20, keyword: str | None = None):
    query = db.query(models.Hospital)
    if keyword:
        keyword = keyword.strip()
        query = query.filter(
            models.Hospital.name.ilike(f"%{keyword}%")
            | models.Hospital.phone.ilike(f"%{keyword}%")
            | models.Hospital.address.ilike(f"%{keyword}%")
        )
    query = query.order_by(models.Hospital.id.desc())
    return _paginate(query, skip, limit)


def update_hospital(db: Session, hospital_id: int, hospital_update: schemas.HospitalUpdate):
    hospital = get_hospital(db, hospital_id)
    if hospital is None:
        return None

    update_data = hospital_update.model_dump(exclude_unset=True)
    _apply_updates(hospital, update_data)
    db.commit()
    db.refresh(hospital)
    return hospital


def delete_hospital(db: Session, hospital_id: int):
    hospital = get_hospital(db, hospital_id)
    if hospital is None:
        return None

    db.query(models.HealthRecord).filter(models.HealthRecord.hospital_id == hospital.id).update(
        {models.HealthRecord.hospital_id: None}, synchronize_session=False
    )
    db.delete(hospital)
    db.commit()
    return hospital


# pet CRUD

def create_pet(db: Session, pet: schemas.PetCreate):
    payload = pet.model_dump()
    owner = _get_owner_or_none(db, payload.get("owner_id"))
    if payload.get("owner_id") is not None and owner is None:
        raise ValueError("Owner not found")
    if owner is not None:
        payload["owner_name"] = owner.name

    db_pet = models.Pet(**payload)
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet


def get_pet(db: Session, pet_id: int):
    return db.query(models.Pet).filter(models.Pet.id == pet_id).first()


def get_pets_paginated(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    species: str | None = None,
    sex: str | None = None,
    sterilized: bool | None = None,
    owner_name: str | None = None,
    keyword: str | None = None,
):
    query = db.query(models.Pet)

    if species:
        query = query.filter(models.Pet.species == species)
    if sex:
        query = query.filter(models.Pet.sex == sex)
    if sterilized is not None:
        query = query.filter(models.Pet.sterilized == sterilized)
    if owner_name:
        query = query.filter(models.Pet.owner_name.ilike(f"%{owner_name.strip()}%"))
    if keyword:
        keyword = keyword.strip()
        query = query.filter(
            models.Pet.name.ilike(f"%{keyword}%")
            | models.Pet.breed.ilike(f"%{keyword}%")
            | models.Pet.special_notes.ilike(f"%{keyword}%")
        )

    query = query.order_by(models.Pet.id.desc())
    return _paginate(query, skip, limit)


def update_pet(db: Session, pet_id: int, pet_update: schemas.PetUpdate):
    pet = get_pet(db, pet_id)
    if pet is None:
        return None

    update_data = pet_update.model_dump(exclude_unset=True)
    if "owner_id" in update_data:
        owner = _get_owner_or_none(db, update_data["owner_id"])
        if update_data["owner_id"] is not None and owner is None:
            raise ValueError("Owner not found")
        if owner is not None and "owner_name" not in update_data:
            update_data["owner_name"] = owner.name

    _apply_updates(pet, update_data)
    db.commit()
    db.refresh(pet)
    return pet


def delete_pet(db: Session, pet_id: int):
    pet = get_pet(db, pet_id)
    if pet is None:
        return None

    db.delete(pet)
    db.commit()
    return pet


# health record CRUD

def create_health_record(db: Session, pet_id: int, record: schemas.HealthCreate):
    payload = record.model_dump()
    hospital = _get_hospital_or_none(db, payload.get("hospital_id"))
    if payload.get("hospital_id") is not None and hospital is None:
        raise ValueError("Hospital not found")

    db_record = models.HealthRecord(pet_id=pet_id, **payload)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_health_record(db: Session, pet_id: int, record_id: int):
    return (
        db.query(models.HealthRecord)
        .filter(
            models.HealthRecord.pet_id == pet_id,
            models.HealthRecord.id == record_id,
        )
        .first()
    )


def get_health_records_paginated(
    db: Session,
    pet_id: int,
    skip: int = 0,
    limit: int = 20,
    start_date: date | None = None,
    end_date: date | None = None,
    min_cost: float | None = None,
    max_cost: float | None = None,
    keyword: str | None = None,
):
    query = db.query(models.HealthRecord).filter(models.HealthRecord.pet_id == pet_id)

    if start_date:
        query = query.filter(models.HealthRecord.record_date >= start_date)
    if end_date:
        query = query.filter(models.HealthRecord.record_date <= end_date)
    if min_cost is not None:
        query = query.filter(models.HealthRecord.cost >= min_cost)
    if max_cost is not None:
        query = query.filter(models.HealthRecord.cost <= max_cost)
    if keyword:
        keyword = keyword.strip()
        query = query.filter(
            models.HealthRecord.symptom.ilike(f"%{keyword}%")
            | models.HealthRecord.treatment.ilike(f"%{keyword}%")
            | models.HealthRecord.diagnosis.ilike(f"%{keyword}%")
            | models.HealthRecord.prescription.ilike(f"%{keyword}%")
            | models.HealthRecord.veterinarian_name.ilike(f"%{keyword}%")
        )

    query = query.order_by(models.HealthRecord.record_date.desc(), models.HealthRecord.id.desc())
    return _paginate(query, skip, limit)


def update_health_record(
    db: Session,
    pet_id: int,
    record_id: int,
    record_update: schemas.HealthUpdate,
):
    record = get_health_record(db, pet_id, record_id)
    if record is None:
        return None

    update_data = record_update.model_dump(exclude_unset=True)
    if "hospital_id" in update_data:
        hospital = _get_hospital_or_none(db, update_data["hospital_id"])
        if update_data["hospital_id"] is not None and hospital is None:
            raise ValueError("Hospital not found")

    _apply_updates(record, update_data)
    db.commit()
    db.refresh(record)
    return record


def delete_health_record(db: Session, pet_id: int, record_id: int):
    record = get_health_record(db, pet_id, record_id)
    if record is None:
        return None

    db.delete(record)
    db.commit()
    return record


# vaccination CRUD

def create_vaccination(db: Session, pet_id: int, vaccine: schemas.VaccinationCreate):
    db_vaccine = models.Vaccination(pet_id=pet_id, **vaccine.model_dump())
    db.add(db_vaccine)
    db.commit()
    db.refresh(db_vaccine)
    return db_vaccine


def get_vaccination(db: Session, pet_id: int, vaccination_id: int):
    return (
        db.query(models.Vaccination)
        .filter(
            models.Vaccination.pet_id == pet_id,
            models.Vaccination.id == vaccination_id,
        )
        .first()
    )


def get_vaccinations(db: Session, pet_id: int, skip: int = 0, limit: int = 1000):
    return (
        db.query(models.Vaccination)
        .filter(models.Vaccination.pet_id == pet_id)
        .order_by(models.Vaccination.next_due_date.asc(), models.Vaccination.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_vaccinations_paginated(
    db: Session,
    pet_id: int,
    skip: int = 0,
    limit: int = 20,
    vaccine_name: str | None = None,
    status: schemas.VaccinationStatusFilter | None = None,
    next_due_from: date | None = None,
    next_due_to: date | None = None,
):
    query = db.query(models.Vaccination).filter(models.Vaccination.pet_id == pet_id)

    if vaccine_name:
        query = query.filter(models.Vaccination.vaccine_name.ilike(f"%{vaccine_name.strip()}%"))
    if next_due_from:
        query = query.filter(models.Vaccination.next_due_date >= next_due_from)
    if next_due_to:
        query = query.filter(models.Vaccination.next_due_date <= next_due_to)

    today = date.today()
    due_soon_boundary = today + timedelta(days=DUE_SOON_DAYS)
    if status == schemas.VaccinationStatusFilter.overdue:
        query = query.filter(models.Vaccination.next_due_date < today)
    elif status == schemas.VaccinationStatusFilter.due_soon:
        query = query.filter(
            models.Vaccination.next_due_date >= today,
            models.Vaccination.next_due_date <= due_soon_boundary,
        )
    elif status == schemas.VaccinationStatusFilter.valid:
        query = query.filter(models.Vaccination.next_due_date > due_soon_boundary)

    query = query.order_by(models.Vaccination.next_due_date.asc(), models.Vaccination.id.desc())
    return _paginate(query, skip, limit)


def update_vaccination(
    db: Session,
    pet_id: int,
    vaccination_id: int,
    vaccine_update: schemas.VaccinationUpdate,
):
    vaccine = get_vaccination(db, pet_id, vaccination_id)
    if vaccine is None:
        return None

    update_data = vaccine_update.model_dump(exclude_unset=True)
    _validate_vaccination_patch(vaccine, update_data)
    _apply_updates(vaccine, update_data)
    db.commit()
    db.refresh(vaccine)
    return vaccine


def delete_vaccination(db: Session, pet_id: int, vaccination_id: int):
    vaccine = get_vaccination(db, pet_id, vaccination_id)
    if vaccine is None:
        return None

    db.delete(vaccine)
    db.commit()
    return vaccine


# schedule CRUD

def create_schedule(db: Session, pet_id: int, schedule: schemas.ScheduleCreate):
    db_schedule = models.Schedule(pet_id=pet_id, **schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def get_schedule(db: Session, pet_id: int, schedule_id: int):
    return (
        db.query(models.Schedule)
        .filter(
            models.Schedule.pet_id == pet_id,
            models.Schedule.id == schedule_id,
        )
        .first()
    )


def get_schedules_paginated(
    db: Session,
    pet_id: int,
    skip: int = 0,
    limit: int = 20,
    event_type: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
):
    query = db.query(models.Schedule).filter(models.Schedule.pet_id == pet_id)

    if event_type:
        query = query.filter(models.Schedule.event_type == event_type)
    if from_date:
        query = query.filter(models.Schedule.schedule_date >= from_date)
    if to_date:
        query = query.filter(models.Schedule.schedule_date <= to_date)

    query = query.order_by(models.Schedule.schedule_date.asc(), models.Schedule.id.desc())
    return _paginate(query, skip, limit)


def update_schedule(
    db: Session,
    pet_id: int,
    schedule_id: int,
    schedule_update: schemas.ScheduleUpdate,
):
    schedule = get_schedule(db, pet_id, schedule_id)
    if schedule is None:
        return None

    update_data = schedule_update.model_dump(exclude_unset=True)
    _apply_updates(schedule, update_data)
    db.commit()
    db.refresh(schedule)
    return schedule


def delete_schedule(db: Session, pet_id: int, schedule_id: int):
    schedule = get_schedule(db, pet_id, schedule_id)
    if schedule is None:
        return None

    db.delete(schedule)
    db.commit()
    return schedule


# reports and insights

def get_cost_report(db: Session, pet_id: int):
    health_cost = (
        db.query(func.sum(models.HealthRecord.cost))
        .filter(models.HealthRecord.pet_id == pet_id)
        .scalar()
        or 0
    )
    vaccine_cost = (
        db.query(func.sum(models.Vaccination.cost))
        .filter(models.Vaccination.pet_id == pet_id)
        .scalar()
        or 0
    )
    total_cost = health_cost + vaccine_cost

    return {
        "health_cost": health_cost,
        "vaccination_cost": vaccine_cost,
        "total_cost": total_cost,
    }


def get_vaccine_report(db: Session, pet_id: int):
    vaccines = get_vaccinations(db, pet_id)
    today = date.today()
    due_soon_boundary = today + timedelta(days=DUE_SOON_DAYS)
    report = []

    for v in vaccines:
        if v.next_due_date < today:
            status = "overdue"
        elif v.next_due_date <= due_soon_boundary:
            status = "due_soon"
        else:
            status = "valid"

        report.append(
            {
                "vaccine_name": v.vaccine_name,
                "last_vaccination": v.vaccination_date,
                "next_due": v.next_due_date,
                "status": status,
            }
        )

    return report


def get_recommendation(db: Session, pet_id: int):
    pet = get_pet(db, pet_id)
    if pet is None:
        return None

    vaccines = get_vaccinations(db, pet_id)
    recommendations = []
    today = date.today()
    age = calculate_age(pet.birth_date)

    if age >= 12:
        recommendations.append("노령 반려동물 건강검진을 권장합니다.")

    emergency_visit_count = (
        db.query(models.HealthRecord)
        .filter(
            models.HealthRecord.pet_id == pet_id,
            models.HealthRecord.severity == schemas.SeverityEnum.emergency,
        )
        .count()
    )
    if emergency_visit_count > 0:
        recommendations.append("응급 진료 이력이 있어 정기적인 경과 관찰을 권장합니다.")

    for v in vaccines:
        if v.next_due_date < today:
            recommendations.append(f"{v.vaccine_name} 백신 재접종이 필요합니다.")

    if not recommendations:
        recommendations.append("현재 특별한 건강 권장사항이 없습니다.")

    return {"pet_name": pet.name, "age": age, "recommendations": recommendations}


def create_overdue_vaccination_schedules(db: Session, pet_id: int):
    pet = get_pet(db, pet_id)
    if pet is None:
        return None

    vaccines = get_vaccinations(db, pet_id)
    today = date.today()
    created = []

    for v in vaccines:
        if v.next_due_date < today:
            exists = (
                db.query(models.Schedule)
                .filter(
                    models.Schedule.pet_id == pet_id,
                    models.Schedule.event_type == "vaccine",
                    models.Schedule.description == f"{v.vaccine_name} 재접종",
                    models.Schedule.schedule_date == today,
                )
                .first()
            )
            if exists:
                continue

            schedule = models.Schedule(
                pet_id=pet_id,
                event_type="vaccine",
                description=f"{v.vaccine_name} 재접종",
                schedule_date=today,
            )
            db.add(schedule)
            created.append(schedule)

    if created:
        db.commit()
        for schedule in created:
            db.refresh(schedule)

    return created


def get_health_prediction(db: Session, pet_id: int):
    pet = get_pet(db, pet_id)
    if pet is None:
        return None

    health_records = (
        db.query(models.HealthRecord)
        .filter(models.HealthRecord.pet_id == pet_id)
        .order_by(models.HealthRecord.record_date.desc(), models.HealthRecord.id.desc())
        .all()
    )
    vaccinations = get_vaccinations(db, pet_id)

    age = calculate_age(pet.birth_date)
    vaccinated = infer_vaccinated(vaccinations)
    sterilized = infer_sterilized(pet, health_records)
    size = infer_size(pet.weight)
    risk = predict_health_risk(age, vaccinated, sterilized, size)

    recommendation = (
        "건강 위험 가능성이 있습니다. 수의사 검진을 권장합니다."
        if risk == 1
        else "현재 건강 상태는 비교적 양호합니다."
    )

    return {
        "pet_id": pet.id,
        "pet_name": pet.name,
        "features_used": {
            "age": age,
            "vaccinated": vaccinated,
            "sterilized": sterilized,
            "size": size,
        },
        "health_risk": risk,
        "recommendation": recommendation,
    }


def calculate_age(birth_date: date) -> int:
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return max(age, 0)


def infer_vaccinated(vaccinations) -> int:
    today = date.today()
    return 1 if any(v.next_due_date and v.next_due_date >= today for v in vaccinations) else 0


def infer_sterilized(pet, health_records) -> int:
    if pet.sterilized:
        return 1

    keywords = ["중성화", "neuter", "spay", "sterilized"]
    for r in health_records:
        symptom_text = (r.symptom or "").lower()
        treatment_text = (r.treatment or "").lower()
        joined = f"{symptom_text} {treatment_text}"
        if any(keyword in joined for keyword in keywords):
            return 1
    return 0


def infer_size(weight: float) -> int:
    if weight < 5:
        return 0
    if weight < 15:
        return 1
    return 2
