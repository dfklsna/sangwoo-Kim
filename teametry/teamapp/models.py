# teamapp/models.py – 데이터베이스 모델 정의
from django.db import models

# 여기서 조 랑 방의 개념을 다르게 사용: 조는 1조, 2조 등 각 조를 의미
# 방은 모든 조를 포함한 전체 참가자가 모인 곳

# 방 정보 저장
class Team(models.Model): #Team이라는 모델 정의 시작
    #방 유형 선택: 개발/일반
    TEAM_TYPES = [
        ('development', '개발'),
        ('general', '일반'),
    ]
    # 팀 나누는 방식: 조 당 인원수/ 조 개수
    DIVISION_CHOICES = [
        ('BY_MEMBER_COUNT', '조 당 인원 수'),# 예: 한 조에 최대 4명
        ('BY_TEAM_COUNT', '조 개수'), # 예: 총 5개의 조
    ]

    team_type = models.CharField(max_length=20, choices=TEAM_TYPES)     # 조 유형
    division_type = models.CharField(max_length=20, choices=DIVISION_CHOICES)  # 나누는 방식
    room_code = models.CharField(max_length=10)            # 방 코드
    password = models.CharField(max_length=100)                         # 비밀번호
    max_members = models.PositiveIntegerField(null=True, blank=True)    # 조 당 인원 수 (선택)
    total_teams = models.PositiveIntegerField(null=True, blank=True)    # 조 개수 (선택)
    total_members = models.PositiveIntegerField()                       # 총 인원
    created_at = models.DateTimeField(auto_now_add=True)  # 방 생성 요청 시각 자동 기록

    # 최종 확정 여부(기본 False)
    is_assign_finalized = models.BooleanField(default=False)

# 참가자 정보 저장
class Participant(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)         # 어떤 방에 참가했는지
    name = models.CharField(max_length=30)                           # 이름
    student_id = models.CharField(max_length=20)                     # 학번
    email = models.EmailField()                                      # 이메일
    phone_number = models.CharField(max_length=20)                   # 전화번호

    # 역할 선택지: 프론트/백엔드/ 선택 안함
    POSITION_CHOICES = [
        ('frontend', '프론트엔드'),
        ('backend', '백엔드'),
        ('none', '선택 안 함'),
    ]
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default='none'  # 일반 팀이거나 선택 안 한 경우
    )  # 역할 선택

    assigned_position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default='none'  # 조 편성 시 자동 분류된 역할
    )  # 실제 조 편성에 반영되는 역할

    leader_preference = models.BooleanField(default=False)  # 리더 희망 여부
    created_at = models.DateTimeField(auto_now_add=True)   # 제출 시각 자동 기록
    is_leader = models.BooleanField(default=False)  # 실제 리더 여부 (조 편성 결과 반영)             

    assigned_team_number = models.IntegerField(null=True, blank=True)  # 조 편성된 팀 번호

# 성격 검사 결과 요약 저장
class SurveyResponse(models.Model):
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)  # 1:1로 참가자와 연결

    # Big Five 요약 점수 (100점 만점 기준)
    openness = models.IntegerField()
    conscientiousness = models.IntegerField()

    # MBTI 차원별 점수 (기준점: 0, +면 앞쪽 유형, -면 반대)
    mbti_ie_score = models.FloatField()
    mbti_sn_score = models.FloatField()
    mbti_tf_score = models.FloatField()
    mbti_jp_score = models.FloatField()

    inferred_mbti = models.CharField(
    max_length=4
)  # 점수 기반으로 추론된 최종 MBTI 유형(예: INTP), 항상 값이 들어가야 함(필수)
    submitted_at = models.DateTimeField(auto_now_add=True)  # 제출 시간 자동 저장

    def __str__(self):
        return f"{self.participant.name} ({self.inferred_mbti})"

