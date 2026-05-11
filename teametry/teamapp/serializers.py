# teamapp/serializers.py – API 요청/응답 포맷 정의
from rest_framework import serializers
from .models import Team, Participant, SurveyResponse


class TeamCreateSerializer(serializers.Serializer):
    team_type = serializers.ChoiceField(choices=["development", "general"])
    division_type = serializers.ChoiceField(choices=["BY_MEMBER_COUNT", "BY_TEAM_COUNT"])
    total_members = serializers.IntegerField(min_value=1)
    max_members = serializers.IntegerField(min_value=1, required=False)
    total_teams = serializers.IntegerField(min_value=1, required=False)

    def validate(self, data):
        division_type = data.get("division_type")
        total_members = data.get("total_members")
        max_members = data.get("max_members")
        total_teams = data.get("total_teams")

        if division_type == "BY_MEMBER_COUNT":
            if not max_members:
                raise serializers.ValidationError("division_type이 'BY_MEMBER_COUNT'인 경우 max_members는 필수입니다.")
            # ★ 조 인원수가 전체 인원수보다 많을 수 없음
            if max_members > total_members:
                raise serializers.ValidationError("조 인원 수는 전체 인원 수보다 많을 수 없습니다.")

        elif division_type == "BY_TEAM_COUNT":
            if not total_teams:
                raise serializers.ValidationError("division_type이 'BY_TEAM_COUNT'인 경우 total_teams는 필수입니다.")
            # ★ 조의 갯수가 전체 인원수보다 많을 수 없음
            if total_teams > total_members:
                raise serializers.ValidationError("조의 갯수는 전체 인원 수보다 많을 수 없습니다.")

        else:
            raise serializers.ValidationError("division_type 값이 유효하지 않습니다.")

        return data



# 방 생성 완료 시 관리자에게 반환할 응답 Serializer
class TeamResponseSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()  # 링크는 room_code로 동적 생성

    class Meta:
        model = Team
        fields = ["room_code", "password", "link"]
        # 응답에 포함될 필드: 방코드, 비밀번호, 링크

    def get_link(self, obj):
        return f"https://teametry.kr/team/{obj.room_code}"  # 링크 규칙

# 참가자가 방에 입장할 때 방 코드 유효성 확인
class RoomJoinSerializer(serializers.Serializer):
    room_code = serializers.CharField(max_length=10)

    def validate_room_code(self, value):
        """
        입력받은 방 코드로 Team을 찾고 self.team에 저장.
        존재하지 않으면 validation error 반환.
        """
        team_qs = Team.objects.filter(room_code=value)
        if not team_qs.exists():
            raise serializers.ValidationError("유효하지 않은 방 코드입니다.")
        self.team = team_qs.first()
        return value



# 참가자 정보 입력용 Serializer
class ParticipantCreateSerializer(serializers.ModelSerializer):
    room_code = serializers.CharField(write_only=True)  # 사용자가 입력한 방 코드

    class Meta:
        model = Participant
        fields = [
            "room_code",           # 사용자가 입력한 방 코드 (실제 모델에는 없음)
            "name",                # 이름
            "student_id",          # 학번
            "email",               # 이메일
            "phone_number",        # 전화번호
            "position",            # 선택 역할 (개발팀은 optional, 일반팀은 무조건 none)
            "leader_preference"    # 리더 희망 여부
        ]

    def validate_room_code(self, value):
        """
        입력받은 room_code로 Team(방)을 찾고, self.team에 저장.
        존재하지 않으면 validation error 반환.
        """
        team_qs = Team.objects.filter(room_code=value)
        if not team_qs.exists():
            raise serializers.ValidationError("유효하지 않은 방 코드입니다.")
        self.team = team_qs.first()  # ✅ get → filter().first()로 수정
        return value

    def validate(self, data):
        """
        개발팀이면 position 그대로 둠 (frontend/backend/none 허용),
        일반팀이면 position을 무조건 none으로 강제 세팅.
        """
        team_type = self.team.team_type
        if team_type != "development":
            data["position"] = "none"
        return data

    def create(self, validated_data):
        """
        validated_data에 team 객체를 삽입하고, room_code는 제거.
        최종적으로 Participant 객체를 생성하고 DB에 저장.
        """
        validated_data["team"] = self.team
        validated_data.pop("room_code")
        return Participant.objects.create(**validated_data)


# 성격 검사 결과 저장용 Serializer
class SurveyResponseSerializer(serializers.ModelSerializer):
    participant_id = serializers.IntegerField(write_only=True)  # 참가자 ID만 받아서 내부 연결

    class Meta:
        model = SurveyResponse
        fields = [
            "participant_id", "openness", "conscientiousness",
            "mbti_ie_score", "mbti_sn_score",
            "mbti_tf_score", "mbti_jp_score",
            "inferred_mbti"
        ]

    # 참가자 ID 유효성 확인
    def validate_participant_id(self, value):
        if not Participant.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 참가자입니다.")
        return value

    # participant를 직접 연결하여 생성
    def create(self, validated_data):
        participant_id = validated_data.pop("participant_id")
        participant = Participant.objects.get(id=participant_id)
        return SurveyResponse.objects.create(participant=participant, **validated_data)
