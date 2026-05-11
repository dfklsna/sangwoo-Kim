from django.shortcuts import render
from .utils import get_temperament

# Create your views here.
# views.py – 조 생성 요청 처리 (주석 포함)
import math, random, string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Team, Participant, SurveyResponse
from .serializers import TeamCreateSerializer, TeamResponseSerializer, RoomJoinSerializer, ParticipantCreateSerializer, SurveyResponseSerializer
from .major import assign_developer_teams_final_logic
from .import_random import assign_non_developer_teams_rule_based
from django.shortcuts import get_object_or_404


# 방 코드 및 비밀번호 생성을 위한 랜덤 문자열 생성 함수
def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

class TeamCreateView(APIView):
    def get(self, request):
        return Response({"message": "GET OK"})
    def post(self, request):
        # 1. 요청 데이터 유효성 검사
        serializer = TeamCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        total_members = data['total_members']
        division_type = data['division_type']

        # 2. 나누는 방식에 따라 조 개수와 조당 인원 계산
        if division_type == "BY_MEMBER_COUNT":
            max_members = data['max_members']
            total_teams = math.ceil(total_members / max_members)
        else:  # "BY_TEAM_COUNT"
            total_teams = data['total_teams']
            max_members = math.ceil(total_members / total_teams)

        # 3. 방 단위로 room_code 및 비밀번호 1회 생성
        room_code = generate_code()
        while Team.objects.filter(room_code=room_code).exists():
            room_code = generate_code()

        password = generate_code(8)  # 관리자용 비밀번호

        # ✅ Team 객체 1개만 생성 (방 정보만 담음)
        team = Team.objects.create(
            team_type=data['team_type'],
            division_type=division_type,
            room_code=room_code,  # 방 코드
            password=password,    # 관리자용 비밀번호
            max_members=max_members,
            total_members=total_members,
            total_teams=total_teams if division_type == "BY_TEAM_COUNT" else None,
        )

        # 응답
        response_data = TeamResponseSerializer(team).data
        return Response({"message": "Team created successfully", **response_data}, status=201)




class RoomInfoView(APIView):
    def get(self, request, room_code):
        pw = request.GET.get("pw")

        # 방어 코드: pw 없을 경우
        if not pw:
            return Response({"error": "비밀번호가 필요합니다."}, status=400)

        try:
            # 필터로 예외 없이 조회
            team_qs = Team.objects.filter(room_code=room_code, password=pw)
            if not team_qs.exists():
                return Response({"error": "방이 존재하지 않거나 비밀번호가 틀렸습니다."}, status=404)

            team = team_qs.first()
        except Exception as e:
            print("🔥 RoomInfoView 오류:", str(e))  # <- 서버 로그에 찍힘
            return Response({"error": "서버 내부 오류", "detail": str(e)}, status=500)

        return Response({
            "link": f"https://teametry.kr/team/{team.room_code}"
        }, status=200)






class RoomJoinView(APIView):
    def post(self, request):
        # 1. room_code 유효성 검사
        serializer = RoomJoinSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        room_code = serializer.validated_data['room_code']
        team = Team.objects.filter(room_code=room_code).first()
        print(f"[DEBUG] room_code: {room_code}, team: {team}")

        # 2. 해당 room_code가 실제 존재하는지 확인 (예외 발생 방지)
        team = Team.objects.filter(room_code=room_code).first()
        print(f"[DEBUG] room_code: {room_code}, team: {team}")
        if not team:
            return Response({"error": "존재하지 않는 방 코드입니다."}, status=404)


        # 3. 입장 성공 시 방 정보 응답
        return Response({
    "message": "방 입장에 성공했습니다.",
    "room_code": team.room_code,
    "team_type": team.team_type,
    "division_type": team.division_type,  
    "max_members": team.max_members if team.division_type == "BY_MEMBER_COUNT" else None,
    "total_teams": team.total_teams if team.division_type == "BY_TEAM_COUNT" else None,
    "total_members": team.total_members
}, status=status.HTTP_200_OK)


# 참가자 정보 등록 처리 API
class ParticipantJoinView(APIView):
    def post(self, request):
        serializer = ParticipantCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # serializer에서 self.team을 잡아두고 있으므로
        team = serializer.team  # ✅ 바로 team 할당

        # 여기서 현재 인원 수 체크!
        current_count = Participant.objects.filter(team=team).count()
        print(f"현재 참가자 수: {current_count}, 최대 인원: {team.total_members}")  # (터미널에서 확인)

        if current_count >= team.total_members:
            return Response({"error": "최대 인원수를 초과했습니다."}, status=status.HTTP_400_BAD_REQUEST)

        participant = serializer.save()

        return Response({
            "message": "참가자 정보가 성공적으로 등록되었습니다.",
            "user_id": participant.id
        }, status=201)



# 참가자가 성격 검사 결과를 제출하는 API
class SurveySubmitView(APIView):
    def post(self, request):
        serializer = SurveyResponseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        survey = serializer.save()  # 결과 저장

        return Response({
            "message": "성격 검사 결과가 성공적으로 저장되었습니다.",
            "survey_id": survey.id
        }, status=201)
    
class SurveyStatusView(APIView):
    def post(self, request):
        room_code = request.data.get("room_code")
        password = request.data.get("password")

        team = Team.objects.filter(room_code=room_code).first()
        if not team:
            return Response({"error": "존재하지 않는 방 코드입니다."}, status=400)
        if team.password != password:
            return Response({"error": "비밀번호가 올바르지 않습니다."}, status=403)

        total_members = team.total_members

        # Team 하나만 집계
        responded = SurveyResponse.objects.filter(participant__team=team).count()
        submitted_ids = SurveyResponse.objects.filter(participant__team=team).values_list("participant_id", flat=True)
        submitted_participants = Participant.objects.filter(id__in=submitted_ids)
        submitted_names = [p.name for p in submitted_participants]

        return Response({
            "room_code": room_code,
            "total": len(submitted_names),   # 실제 설문 완료 수
            "responded": responded,
            "total_members": total_members,  # 분모
            "progress": f"{responded} / {total_members}",
            "submitted": submitted_names,
            "is_assign_finalized": team.is_assign_finalized,  # ✅ 반드시 추가!
        }, status=200)




class TeamAssignView(APIView):
    def post(self, request):
        room_code = request.data.get("room_code")
        password = request.data.get("password")

        # 1. 방(Team) 찾기
        team = Team.objects.filter(room_code=room_code).first()
        if not team:
            return Response({"error": "존재하지 않는 방 코드입니다."}, status=400)
        if team.password != password:
            return Response({"error": "비밀번호가 올바르지 않습니다."}, status=403)

        # 2. 이미 조 편성 완료된 방이면 재배정 불가
        if team.is_assign_finalized:
            return Response({"error": "이미 조 편성이 완료된 방입니다."}, status=400)

        # 3. 참가자/설문 응답 조회
        participants = Participant.objects.filter(team=team)
        responses = SurveyResponse.objects.filter(participant__team=team)

        # 4. 설문 미제출자 존재 여부 확인
        if participants.count() != responses.count():
            return Response({"error": "아직 설문을 완료하지 않은 참가자가 있습니다."}, status=400)

        # 5. 응답 매핑
        response_map = {res.participant_id: res for res in responses}

        # 6. 참가자 정보 리스트화 (리더/MBTI/포지션 등 자동 추론)
        students = []
        for p in participants:
            res = response_map.get(p.id)
            if not res:
                continue

            mbti_str = res.inferred_mbti.upper() if res.inferred_mbti else ""
            ei = mbti_str[0] if mbti_str else ""
            temperament = get_temperament(mbti_str)

            # 포지션/role 자동 지정
            position = p.position
            role = p.position
            if (not position or position == "none") and mbti_str:
                if mbti_str[:2] == "IF":
                    position = "frontend"
                    role = "frontend"
                elif mbti_str[:2] in ("IT", "ET"):
                    position = "backend"
                    role = "backend"
                else:
                    position = "frontend"
                    role = "frontend"

            student = {
                "id": p.id,
                "name": p.name,
                "student_id": p.student_id,
                "email": p.email,
                "phone_number": p.phone_number,
                "role": role,
                "position": position,
                "leader": p.leader_preference,
                "ei": ei,
                "temperament": temperament,
                "wants_leader": p.leader_preference,
                "openness": res.openness,
                "conscientiousness": res.conscientiousness,
                "leader_score": res.openness + res.conscientiousness,
                "mbti": res.inferred_mbti,
            }
            students.append(student)

        # 7. division_type, max_members, total_teams 추출
        division_type = getattr(team, "division_type", None)
        max_members = getattr(team, "max_members", None)
        total_teams = getattr(team, "total_teams", None)

        # 8. 팀 유형에 따라 배정 알고리즘 분기
        if team.team_type == "development":
            teams, team_leaders_info = assign_developer_teams_final_logic(
                students,
                division_type=division_type,
                max_members=max_members,
                total_teams=total_teams
            )
        else:
            teams, team_leaders_info = assign_non_developer_teams_rule_based(
                students,
                division_type=division_type,
                max_members=max_members,
                total_teams=total_teams
            )

        # 9. DB에 참가자 정보 업데이트
        Participant.objects.filter(team=team).update(is_leader=False)
        for team_index, team_group in enumerate(teams, start=1):
            for member in team_group:
                Participant.objects.filter(id=member["id"]).update(
                    assigned_position=member.get("position") or member.get("role") or "",
                    assigned_team_number=team_index
                )
            # 각 팀별 리더 지정
            if team_leaders_info:
                leader_info = team_leaders_info[team_index-1]
                if isinstance(leader_info, dict) and "id" in leader_info:
                    Participant.objects.filter(id=leader_info["id"]).update(is_leader=True)
                elif isinstance(leader_info, int):
                    Participant.objects.filter(id=leader_info).update(is_leader=True)
                elif team_group:
                    Participant.objects.filter(id=team_group[0]["id"]).update(is_leader=True)


        # 11. 결과 반환
        return Response({
            "message": "조 편성이 완료되었습니다.",
            "teams": teams,
            "leaders": team_leaders_info
        }, status=200)




class TeamResultView(APIView):
    def post(self, request):
        room_code = request.data.get("room_code")
        password = request.data.get("password")

        team = Team.objects.filter(room_code=room_code).first()
        if not team:
            return Response({"error": "존재하지 않는 방 코드입니다."}, status=400)

        if team.password != password:
            return Response({"error": "비밀번호가 올바르지 않습니다."}, status=403)

        participants = Participant.objects.filter(team=team).select_related('surveyresponse')

        result = {}

        for p in participants:
            team_num = p.assigned_team_number
            if team_num is None:
                continue

            # SurveyResponse에서 점수와 mbti 추출 (없으면 0/빈문자 처리)
            try:
                survey = p.surveyresponse
                openness = survey.openness
                conscientiousness = survey.conscientiousness
                mbti = survey.inferred_mbti
            except Exception:
                openness = 0
                conscientiousness = 0
                mbti = ""

            if team_num not in result:
                result[team_num] = []

            result[team_num].append({
                "id": p.id,
                "name": p.name,
                "student_id": p.student_id,
                "email": p.email,
                "phone_number": p.phone_number,
                "position": p.assigned_position,
                "is_leader": p.is_leader,
                "openness": openness,
                "conscientiousness": conscientiousness,
                "mbti": mbti,
            })

        sorted_result = dict(sorted(result.items()))

        return Response({
            "message": "조 편성 결과 조회 성공",
            "teams": sorted_result,
            "is_finalized": team.is_assign_finalized,
        }, status=200)



class TeamChangeView(APIView):
    def post(self, request):
        room_code = request.data.get("room_code")
        password = request.data.get("password")
        teams = request.data.get("teams", {})
        finalize = request.data.get("finalize", False)  # ✅ 최종 확정 버튼 눌렀는지 여부(프론트에서 전달)

        #  해당 room_code의 모든 Team 가져오기!
        qs = Team.objects.filter(room_code=room_code)
        if not qs.exists():
            return Response({"error": "존재하지 않는 방입니다."}, status=400)
        
        # 모든 team password 같다고 가정(동일 방이니까)
        any_team = qs.first()
        if any_team.password != password:
            return Response({"error": "비밀번호가 올바르지 않습니다."}, status=403)

        # 이미 최종 확정된 경우 수정 불가 (모든 팀이 동일 방이므로 하나만 체크)
        if any_team.is_assign_finalized:
            return Response({"error": "조 편성이 최종 확정되어 더이상 변경할 수 없습니다."}, status=403)

        # 참가자 전체 리더 초기화 (이 방에 소속된 모든 참가자)
        Participant.objects.filter(team__room_code=room_code).update(is_leader=False)

        # 전달받은 teams 구조로 참가자 정보 일괄 업데이트
        for team_number, members in teams.items():
            for member in members:
                participant_id = member.get("participant_id")
                position = member.get("position")
                is_leader = member.get("is_leader", False)

                try:
                    # 조와 상관없이 해당 방(room_code)에 속한 참가자 대상으로만 업데이트!
                    p = Participant.objects.get(id=participant_id, team__room_code=room_code)
                    p.assigned_team_number = int(team_number)
                    p.assigned_position = position
                    p.is_leader = is_leader
                    p.save()
                except Participant.DoesNotExist:
                    continue  # 잘못된 참가자 ID는 무시

        # ✅ 완료 버튼이 눌린 경우, 각 조에 조장이 반드시 1명씩 있는지 검증
        if finalize:
            for team_number, members in teams.items():
                leader_count = sum([1 for m in members if m.get("is_leader", False)])
                if leader_count == 0:
                    return Response({
                        "error": f"{team_number}조에 조장이 지정되지 않았습니다. 각 조마다 반드시 1명의 조장이 필요합니다."
                    }, status=400)
                if leader_count > 1:
                    return Response({
                        "error": f"{team_number}조에 조장이 2명 이상 지정되어 있습니다. 각 조마다 반드시 1명의 조장만 지정하세요."
                    }, status=400)
            qs.update(is_assign_finalized=True)

        return Response({"message": "조 편성 결과가 성공적으로 반영되었습니다."}, status=200)



# 특정 팀 상세 정보 조회 (result2.html 용)
class TeamDetailView(APIView):
    def get(self, request, room_code: str, team_number: int):
        #  DB에서 직접 필터링: 해당 방 + 해당 조 번호
        team_members = Participant.objects.filter(
            team__room_code=room_code,
            assigned_team_number=team_number
        )

        if not team_members.exists():
            return Response({"error": "해당 팀에 속한 참가자가 없습니다."}, status=404)

        member_list = []
        for p in team_members:
            member_list.append({
                "id": p.id,
                "name": p.name,
                "student_id": p.student_id,
                "email": p.email,
                "phone_number": p.phone_number,
                "position": p.assigned_position,
                "is_leader": p.is_leader  
            })

        return Response({
            "team_number": team_number,
            "members": member_list
        }, status=200)



#  참가자 성격/역할 요약 설명 API (자연어 요약)
class ParticipantSummaryView(APIView):
    def get(self, request, participant_id: int):
        try:
            p = Participant.objects.get(id=participant_id)
            s = SurveyResponse.objects.get(participant=p)
        except (Participant.DoesNotExist, SurveyResponse.DoesNotExist):
            return Response({"error": "해당 참가자 또는 설문 결과가 없습니다."}, status=404)

        # 자연어 요약 생성
        lines = [
            f"{p.name}님은 {p.position} 역할을 희망하며,",
            f"조장 역할 {'선호합니다' if p.leader_preference else '선호하지 않습니다'}."
        ]

        if s.openness >= 70:
            lines.append("새로운 아이디어와 다양한 경험을 즐기는 개방성이 높은 성격입니다.")
        elif s.openness <= 30:
            lines.append("익숙하고 안정적인 방식을 선호하는 성향입니다.")

        if s.conscientiousness >= 70:
            lines.append("매우 책임감 있고 계획적인 태도를 갖고 있습니다.")
        elif s.conscientiousness <= 30:
            lines.append("즉흥적이고 융통성 있는 성격입니다.")

        lines.append(f"MBTI 유형은 {s.inferred_mbti}입니다.")

        return Response({
            "participant_id": p.id,
            "summary": " ".join(lines)
        }, status=200)

# teamapp/views.py
from django.http import JsonResponse

def test_api(request):
    return JsonResponse({"message": "연동 성공!"})


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Team, Participant

class TeamListView(APIView):
    def get(self, request):
        room_code = request.query_params.get("room_code")
        password = request.query_params.get("password")

        try:
            team = Team.objects.get(room_code=room_code)
        except Team.DoesNotExist:
            return Response({"error": "존재하지 않는 방입니다."}, status=400)

        if team.password != password:
            return Response({"error": "비밀번호가 올바르지 않습니다."}, status=403)

        # 팀별 참가자 구성
        team_data = {}
        participants = Participant.objects.filter(team=team).order_by("assigned_team_number")

        for p in participants:
            team_num = p.assigned_team_number
            if team_num not in team_data:
                team_data[team_num] = []
            team_data[team_num].append({
                "id": p.id,
                "name": p.name,
                "position": p.assigned_position,
                "is_leader": p.is_leader,
            })

        return Response({
            "message": "팀 목록 조회 성공",
            "teams": team_data
        }, status=200)



# views.py
from django.http import JsonResponse

def test_connection(request):
    return JsonResponse({"message": "백엔드 연결 성공!"})
