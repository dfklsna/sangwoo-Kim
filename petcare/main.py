from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

import crud
import schemas
from database import Base, SessionLocal, engine, run_startup_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_startup_migrations()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="반려동물 케어 관리 API",
    description="반려동물 건강 기록, 예방접종, 일정 관리 및 케어 인사이트를 제공하는 API",
    version="1.0.0",
    lifespan=lifespan
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_pet(db: Session, pet_id: int):
    pet = crud.get_pet(db, pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet


def validate_date_range(start_date: date | None, end_date: date | None, start_name: str, end_name: str):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail=f"{start_name} cannot be later than {end_name}")


def validate_cost_range(min_cost: float | None, max_cost: float | None):
    if min_cost is not None and max_cost is not None and min_cost > max_cost:
        raise HTTPException(status_code=400, detail="min_cost cannot be greater than max_cost")


@app.get(
    "/",
    tags=["기본"],
    summary="API 상태 확인",
    description="API 서버가 정상적으로 실행 중인지 확인합니다."
)
def root():
    return {"message": "PetCare API"}


@app.post(
    "/owners",
    tags=["보호자"],
    summary="보호자 등록",
    description="새로운 보호자 정보를 등록합니다.",
    response_model=schemas.Owner,
    status_code=status.HTTP_201_CREATED,
)
def create_owner(owner: schemas.OwnerCreate, db: Session = Depends(get_db)):
    return crud.create_owner(db, owner)


@app.get(
    "/owners",
    tags=["보호자"],
    summary="보호자 목록 조회",
    description="보호자 목록을 조회합니다. 검색어와 페이지네이션을 지원합니다.",
    response_model=schemas.OwnerListResponse,
)
def read_owners(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None, min_length=1, max_length=100),
    db: Session = Depends(get_db),
):
    return crud.get_owners_paginated(db, skip=skip, limit=limit, keyword=keyword)


@app.get(
    "/owners/{owner_id}",
    tags=["보호자"],
    summary="보호자 상세 조회",
    description="특정 보호자의 상세 정보를 조회합니다.",
    response_model=schemas.Owner,
)
def read_owner(owner_id: int, db: Session = Depends(get_db)):
    owner = crud.get_owner(db, owner_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Owner not found")
    return owner


@app.patch(
    "/owners/{owner_id}",
    tags=["보호자"],
    summary="보호자 정보 수정",
    description="특정 보호자의 정보를 수정합니다.",
    response_model=schemas.Owner,
)
def update_owner(owner_id: int, owner_update: schemas.OwnerUpdate, db: Session = Depends(get_db)):
    owner = crud.update_owner(db, owner_id, owner_update)
    if owner is None:
        raise HTTPException(status_code=404, detail="Owner not found")
    return owner


@app.delete(
    "/owners/{owner_id}",
    tags=["보호자"],
    summary="보호자 삭제",
    description="특정 보호자 정보를 삭제합니다.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_owner(owner_id: int, db: Session = Depends(get_db)):
    owner = crud.delete_owner(db, owner_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Owner not found")
    return None


@app.post(
    "/hospitals",
    tags=["병원"],
    summary="병원 등록",
    description="동물병원 정보를 등록합니다.",
    response_model=schemas.Hospital,
    status_code=status.HTTP_201_CREATED,
)
def create_hospital(hospital: schemas.HospitalCreate, db: Session = Depends(get_db)):
    return crud.create_hospital(db, hospital)


@app.get(
    "/hospitals",
    tags=["병원"],
    summary="병원 목록 조회",
    description="병원 목록을 조회합니다. 검색어와 페이지네이션을 지원합니다.",
    response_model=schemas.HospitalListResponse,
)
def read_hospitals(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None, min_length=1, max_length=100),
    db: Session = Depends(get_db),
):
    return crud.get_hospitals_paginated(db, skip=skip, limit=limit, keyword=keyword)


@app.get(
    "/hospitals/{hospital_id}",
    tags=["병원"],
    summary="병원 상세 조회",
    description="특정 병원의 상세 정보를 조회합니다.",
    response_model=schemas.Hospital,
)
def read_hospital(hospital_id: int, db: Session = Depends(get_db)):
    hospital = crud.get_hospital(db, hospital_id)
    if hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital


@app.patch(
    "/hospitals/{hospital_id}",
    tags=["병원"],
    summary="병원 정보 수정",
    description="특정 병원 정보를 수정합니다.",
    response_model=schemas.Hospital,
)
def update_hospital(hospital_id: int, hospital_update: schemas.HospitalUpdate, db: Session = Depends(get_db)):
    hospital = crud.update_hospital(db, hospital_id, hospital_update)
    if hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital


@app.delete(
    "/hospitals/{hospital_id}",
    tags=["병원"],
    summary="병원 삭제",
    description="특정 병원 정보를 삭제합니다.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_hospital(hospital_id: int, db: Session = Depends(get_db)):
    hospital = crud.delete_hospital(db, hospital_id)
    if hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return None


@app.post(
    "/pets",
    tags=["반려동물"],
    summary="반려동물 등록",
    description="새로운 반려동물 정보를 등록합니다.",
    response_model=schemas.Pet,
    status_code=status.HTTP_201_CREATED,
)
def create_pet(pet: schemas.PetCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_pet(db, pet)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get(
    "/pets",
    tags=["반려동물"],
    summary="반려동물 목록 조회",
    description="반려동물 목록을 조회합니다. 다양한 필터와 페이지네이션을 지원합니다.",
    response_model=schemas.PetListResponse,
)
def read_pets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    species: schemas.SpeciesEnum | None = Query(None),
    sex: schemas.SexEnum | None = Query(None),
    sterilized: bool | None = Query(None),
    owner_name: str | None = Query(None, min_length=1, max_length=50),
    keyword: str | None = Query(None, min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    return crud.get_pets_paginated(
        db,
        skip=skip,
        limit=limit,
        species=species,
        sex=sex,
        sterilized=sterilized,
        owner_name=owner_name,
        keyword=keyword,
    )


@app.get(
    "/pets/{pet_id}",
    tags=["반려동물"],
    summary="반려동물 상세 조회",
    description="특정 반려동물의 상세 정보를 조회합니다.",
    response_model=schemas.Pet,
)
def read_pet(pet_id: int, db: Session = Depends(get_db)):
    return require_pet(db, pet_id)


@app.patch(
    "/pets/{pet_id}",
    tags=["반려동물"],
    summary="반려동물 정보 수정",
    description="특정 반려동물의 정보를 수정합니다.",
    response_model=schemas.Pet,
)
def update_pet(pet_id: int, pet_update: schemas.PetUpdate, db: Session = Depends(get_db)):
    try:
        pet = crud.update_pet(db, pet_id, pet_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet


@app.delete(
    "/pets/{pet_id}",
    tags=["반려동물"],
    summary="반려동물 삭제",
    description="특정 반려동물 정보를 삭제합니다.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_pet(pet_id: int, db: Session = Depends(get_db)):
    pet = crud.delete_pet(db, pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    return None


@app.post(
    "/pets/{pet_id}/health-records",
    tags=["건강기록"],
    summary="건강 기록 등록",
    description="특정 반려동물의 건강 기록을 등록합니다.",
    response_model=schemas.Health,
    status_code=status.HTTP_201_CREATED,
)
def create_health(pet_id: int, record: schemas.HealthCreate, db: Session = Depends(get_db)):
    require_pet(db, pet_id)
    try:
        return crud.create_health_record(db, pet_id, record)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get(
    "/pets/{pet_id}/health-records",
    tags=["건강기록"],
    summary="건강 기록 목록 조회",
    description="특정 반려동물의 건강 기록 목록을 조회합니다.",
    response_model=schemas.HealthListResponse,
)
def read_health(
    pet_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    min_cost: float | None = Query(None, ge=0),
    max_cost: float | None = Query(None, ge=0),
    keyword: str | None = Query(None, min_length=1, max_length=100),
    db: Session = Depends(get_db),
):
    require_pet(db, pet_id)
    validate_date_range(start_date, end_date, "start_date", "end_date")
    validate_cost_range(min_cost, max_cost)
    return crud.get_health_records_paginated(
        db,
        pet_id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        min_cost=min_cost,
        max_cost=max_cost,
        keyword=keyword,
    )


@app.get(
    "/pets/{pet_id}/health-records/{record_id}",
    tags=["건강기록"],
    summary="건강 기록 상세 조회",
    description="특정 건강 기록의 상세 정보를 조회합니다.",
    response_model=schemas.Health,
)
def read_health_detail(pet_id: int, record_id: int, db: Session = Depends(get_db)):
    require_pet(db, pet_id)
    record = crud.get_health_record(db, pet_id, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Health record not found")
    return record


@app.patch(
    "/pets/{pet_id}/health-records/{record_id}",
    tags=["건강기록"],
    summary="건강 기록 수정",
    description="특정 건강 기록 정보를 수정합니다.",
    response_model=schemas.Health,
)
def update_health_detail(
    pet_id: int,
    record_id: int,
    record_update: schemas.HealthUpdate,
    db: Session = Depends(get_db),
):
    require_pet(db, pet_id)
    try:
        record = crud.update_health_record(db, pet_id, record_id, record_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if record is None:
        raise HTTPException(status_code=404, detail="Health record not found")
    return record


@app.delete(
    "/pets/{pet_id}/health-records/{record_id}",
    tags=["건강기록"],
    summary="건강 기록 삭제",
    description="특정 건강 기록을 삭제합니다.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_health_detail(pet_id: int, record_id: int, db: Session = Depends(get_db)):
    require_pet(db, pet_id)
    record = crud.delete_health_record(db, pet_id, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Health record not found")
    return None


@app.post(
    "/pets/{pet_id}/vaccinations",
    tags=["예방접종"],
    summary="예방접종 등록",
    description="특정 반려동물의 예방접종 정보를 등록합니다.",
    response_model=schemas.Vaccination,
    status_code=status.HTTP_201_CREATED,
)
def create_vaccination(pet_id: int, vaccine: schemas.VaccinationCreate, db: Session = Depends(get_db)):
    require_pet(db, pet_id)
    return crud.create_vaccination(db, pet_id, vaccine)


@app.get(
    "/pets/{pet_id}/vaccinations",
    tags=["예방접종"],
    summary="예방접종 목록 조회",
    description="특정 반려동물의 예방접종 목록을 조회합니다.",
    response_model=schemas.VaccinationListResponse,
)
def read_vaccinations(
    pet_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    vaccine_name: str | None = Query(None, min_length=1, max_length=100),
    status_filter: schemas.VaccinationStatusFilter | None = Query(None, alias="status"),
    next_due_from: date | None = Query(None),
    next_due_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    require_pet(db, pet_id)
    validate_date_range(next_due_from, next_due_to, "next_due_from", "next_due_to")
    return crud.get_vaccinations_paginated(
        db,
        pet_id,
        skip=skip,
        limit=limit,
        vaccine_name=vaccine_name,
        status=status_filter,
        next_due_from=next_due_from,
        next_due_to=next_due_to,
    )


@app.get(
    "/pets/{pet_id}/vaccinations/{vaccination_id}",
    tags=["예방접종"],
    summary="예방접종 상세 조회",
    description="특정 예방접종 상세 정보를 조회합니다.",
    response_model=schemas.Vaccination,
)
def read_vaccination_detail(
    pet_id: int,
    vaccination_id: int,
    db: Session = Depends(get_db),
):
    require_pet(db, pet_id)
    vaccine = crud.get_vaccination(db, pet_id, vaccination_id)
    if vaccine is None:
        raise HTTPException(status_code=404, detail="Vaccination not found")
    return vaccine


@app.patch(
    "/pets/{pet_id}/vaccinations/{vaccination_id}",
    tags=["예방접종"],
    summary="예방접종 정보 수정",
    description="특정 예방접종 정보를 수정합니다.",
    response_model=schemas.Vaccination,
)
def update_vaccination_detail(
    pet_id: int,
    vaccination_id: int,
    vaccine_update: schemas.VaccinationUpdate,
    db: Session = Depends(get_db),
):
    require_pet(db, pet_id)
    vaccine = crud.update_vaccination(db, pet_id, vaccination_id, vaccine_update)
    if vaccine is None:
        raise HTTPException(status_code=404, detail="Vaccination not found")
    return vaccine


@app.delete(
    "/pets/{pet_id}/vaccinations/{vaccination_id}",
    tags=["예방접종"],
    summary="예방접종 삭제",
    description="특정 예방접종 정보를 삭제합니다.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vaccination_detail(
    pet_id: int,
    vaccination_id: int,
    db: Session = Depends(get_db),
):
    require_pet(db, pet_id)
    vaccine = crud.delete_vaccination(db, pet_id, vaccination_id)
    if vaccine is None:
        raise HTTPException(status_code=404, detail="Vaccination not found")
    return None


@app.post(
    "/pets/{pet_id}/schedules",
    tags=["케어 일정"],
    summary="케어 일정 등록",
    description="특정 반려동물의 케어 일정을 등록합니다.",
    response_model=schemas.Schedule,
    status_code=status.HTTP_201_CREATED,
)
def create_schedule(pet_id: int, schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)):
    require_pet(db, pet_id)
    return crud.create_schedule(db, pet_id, schedule)


@app.get(
    "/pets/{pet_id}/schedules",
    tags=["케어 일정"],
    summary="케어 일정 목록 조회",
    description="특정 반려동물의 케어 일정을 조회합니다.",
    response_model=schemas.ScheduleListResponse,
)
def read_schedules(
    pet_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    event_type: schemas.ScheduleEventTypeEnum | None = Query(None),
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    db: Session = Depends(get_db),
):
    require_pet(db, pet_id)
    validate_date_range(from_date, to_date, "from_date", "to_date")
    return crud.get_schedules_paginated(
        db,
        pet_id,
        skip=skip,
        limit=limit,
        event_type=event_type,
        from_date=from_date,
        to_date=to_date,
    )


@app.get(
    "/pets/{pet_id}/schedules/{schedule_id}",
    tags=["케어 일정"],
    summary="케어 일정 상세 조회",
    description="특정 케어 일정의 상세 정보를 조회합니다.",
    response_model=schemas.Schedule,
)
def read_schedule_detail(
    pet_id: int,
    schedule_id: int,
    db: Session = Depends(get_db),
):
    require_pet(db, pet_id)
    schedule = crud.get_schedule(db, pet_id, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@app.patch(
    "/pets/{pet_id}/schedules/{schedule_id}",
    tags=["케어 일정"],
    summary="케어 일정 수정",
    description="특정 케어 일정을 수정합니다.",
    response_model=schemas.Schedule,
)
def update_schedule_detail(
    pet_id: int,
    schedule_id: int,
    schedule_update: schemas.ScheduleUpdate,
    db: Session = Depends(get_db),
):
    require_pet(db, pet_id)
    schedule = crud.update_schedule(db, pet_id, schedule_id, schedule_update)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@app.delete(
    "/pets/{pet_id}/schedules/{schedule_id}",
    tags=["케어 일정"],
    summary="케어 일정 삭제",
    description="특정 케어 일정을 삭제합니다.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_schedule_detail(
    pet_id: int,
    schedule_id: int,
    db: Session = Depends(get_db),
):
    require_pet(db, pet_id)
    schedule = crud.delete_schedule(db, pet_id, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return None


@app.post(
    "/pets/{pet_id}/schedules/vaccination-reminders",
    tags=["케어 일정"],
    summary="예방접종 알림 일정 생성",
    description="예정일이 지난 예방접종을 기준으로 알림 일정을 자동 생성합니다.",
    response_model=list[schemas.Schedule],
    status_code=status.HTTP_201_CREATED,
)
def create_vaccination_reminder_schedules(pet_id: int, db: Session = Depends(get_db)):
    require_pet(db, pet_id)
    return crud.create_overdue_vaccination_schedules(db, pet_id)


@app.get(
    "/pets/{pet_id}/reports/cost-summary",
    tags=["리포트"],
    summary="진료비 요약 리포트 조회",
    description="특정 반려동물의 진료비 요약 정보를 조회합니다.",
    response_model=schemas.CostSummary,
)
def cost_summary(pet_id: int, db: Session = Depends(get_db)):
    require_pet(db, pet_id)
    return crud.get_cost_report(db, pet_id)


@app.get(
    "/pets/{pet_id}/reports/vaccination-status",
    tags=["리포트"],
    summary="예방접종 상태 리포트 조회",
    description="특정 반려동물의 예방접종 상태를 조회합니다.",
    response_model=list[schemas.VaccinationStatus],
)
def vaccination_status(pet_id: int, db: Session = Depends(get_db)):
    require_pet(db, pet_id)
    return crud.get_vaccine_report(db, pet_id)


@app.get(
    "/pets/{pet_id}/insights/care-recommendations",
    tags=["AI 인사이트"],
    summary="케어 추천 조회",
    description="반려동물 상태를 기반으로 케어 추천 정보를 제공합니다.",
    response_model=schemas.CareRecommendationResponse,
)
def care_recommendations(pet_id: int, db: Session = Depends(get_db)):
    result = crud.get_recommendation(db, pet_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    return result


@app.get(
    "/pets/{pet_id}/insights/health-risk-prediction",
    tags=["AI 인사이트"],
    summary="건강 위험 예측 조회",
    description="반려동물 건강 데이터를 바탕으로 위험도를 예측합니다.",
    response_model=schemas.HealthRiskPredictionResponse,
)
def health_risk_prediction(pet_id: int, db: Session = Depends(get_db)):
    result = crud.get_health_prediction(db, pet_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    return result
