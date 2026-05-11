# API 호출 예시

기본 주소:
```text
http://127.0.0.1:8000
```

아래 예시는 `curl` 기준입니다.

---

## 1. 서버 상태 확인
```bash
curl -X GET "http://127.0.0.1:8000/"
```

응답 예시:
```json
{
  "message": "PetCare API"
}
```

---

## 2. 보호자 등록
```bash
curl -X POST "http://127.0.0.1:8000/owners" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "김상우",
    "phone": "010-1234-5678",
    "email": "sangwoo@example.com",
    "address": "서울시 강남구",
    "notes": "주말 방문 선호"
  }'
```

응답 예시:
```json
{
  "id": 1,
  "name": "김상우",
  "phone": "010-1234-5678",
  "email": "sangwoo@example.com",
  "address": "서울시 강남구",
  "notes": "주말 방문 선호",
  "created_at": "2026-03-14T20:00:00",
  "updated_at": "2026-03-14T20:00:00"
}
```

---

## 3. 병원 등록
```bash
curl -X POST "http://127.0.0.1:8000/hospitals" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "행복동물병원",
    "phone": "02-111-2222",
    "address": "서울시 송파구",
    "notes": "24시간 응급 가능"
  }'
```

---

## 4. 반려동물 등록
`owner_id`를 넣으면 서버에서 `owner_name`을 보호자 이름으로 맞춰줍니다.

```bash
curl -X POST "http://127.0.0.1:8000/pets" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "초코",
    "species": "dog",
    "breed": "푸들",
    "sex": "male",
    "birth_date": "2020-05-10",
    "weight": 4.3,
    "sterilized": true,
    "owner_id": 1,
    "owner_name": "임시값",
    "special_notes": "슬개골 관리 필요"
  }'
```

---

## 5. 반려동물 목록 조회
```bash
curl -X GET "http://127.0.0.1:8000/pets?species=dog&sterilized=true&skip=0&limit=10"
```

---

## 6. 건강기록 등록
```bash
curl -X POST "http://127.0.0.1:8000/pets/1/health-records" \
  -H "Content-Type: application/json" \
  -d '{
    "hospital_id": 1,
    "record_date": "2026-03-01",
    "symptom": "기침 및 식욕 저하",
    "treatment": "내복약 처방 및 경과 관찰",
    "diagnosis": "기관지 염증",
    "prescription": "항생제 5일",
    "veterinarian_name": "이수의",
    "visit_type": "consultation",
    "severity": "medium",
    "cost": 45000
  }'
```

---

## 7. 건강기록 조회
```bash
curl -X GET "http://127.0.0.1:8000/pets/1/health-records?start_date=2026-01-01&end_date=2026-12-31"
```

---

## 8. 예방접종 등록
```bash
curl -X POST "http://127.0.0.1:8000/pets/1/vaccinations" \
  -H "Content-Type: application/json" \
  -d '{
    "vaccine_name": "종합백신",
    "vaccination_date": "2025-03-01",
    "next_due_date": "2026-03-01",
    "cost": 30000
  }'
```

---

## 9. 예방접종 상태 조회
```bash
curl -X GET "http://127.0.0.1:8000/pets/1/reports/vaccination-status"
```

---

## 10. 케어 일정 등록
```bash
curl -X POST "http://127.0.0.1:8000/pets/1/schedules" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "grooming",
    "description": "미용 예약",
    "schedule_date": "2026-03-20"
  }'
```

---

## 11. 미접종 알림 일정 자동 생성
기한이 지난 예방접종이 있으면 오늘 날짜 기준으로 백신 일정이 생성됩니다.

```bash
curl -X POST "http://127.0.0.1:8000/pets/1/schedules/vaccination-reminders"
```

---

## 12. 진료비 요약 리포트 조회
```bash
curl -X GET "http://127.0.0.1:8000/pets/1/reports/cost-summary"
```

응답 예시:
```json
{
  "health_cost": 45000,
  "vaccination_cost": 30000,
  "total_cost": 75000
}
```

---

## 13. 케어 추천 조회
```bash
curl -X GET "http://127.0.0.1:8000/pets/1/insights/care-recommendations"
```

---

## 14. 건강 위험 예측 조회
모델 파일(`health_model.pkl`)이 준비되어 있어야 합니다.

```bash
curl -X GET "http://127.0.0.1:8000/pets/1/insights/health-risk-prediction"
```

응답 예시:
```json
{
  "pet_id": 1,
  "pet_name": "초코",
  "features_used": {
    "age": 5,
    "vaccinated": 1,
    "sterilized": 1,
    "size": 0
  },
  "health_risk": 0,
  "recommendation": "현재 건강 상태는 비교적 양호합니다."
}
```

---

## 15. 반려동물 정보 수정
```bash
curl -X PATCH "http://127.0.0.1:8000/pets/1" \
  -H "Content-Type: application/json" \
  -d '{
    "weight": 4.8,
    "special_notes": "최근 사료 변경"
  }'
```

---

## 16. 오류 예시
존재하지 않는 보호자를 `owner_id`로 넣으면 아래처럼 400 에러가 날 수 있습니다.

```json
{
  "detail": "Owner not found"
}
```

