from collections import Counter
import random
import math

def assign_non_developer_teams_rule_based(students, division_type, max_members=None, total_teams=None):
    n_students = len(students)
    if n_students == 0:
        return [], []

    # --- 1단계: 조 개수 및 팀 크기 계산 ---
    if division_type == "BY_MEMBER_COUNT":
        if max_members is None:
            raise ValueError("BY_MEMBER_COUNT 방식에서는 max_members가 필요합니다.")
        num_final_teams = math.ceil(n_students / max_members)
    elif division_type == "BY_TEAM_COUNT":
        if total_teams is None:
            raise ValueError("BY_TEAM_COUNT 방식에서는 total_teams가 필요합니다.")
        num_final_teams = total_teams
    else:
        raise ValueError("division_type은 'BY_MEMBER_COUNT' 또는 'BY_TEAM_COUNT' 여야 합니다.")

    base_size = n_students // num_final_teams
    target_sizes = [base_size] * num_final_teams
    for i in range(n_students % num_final_teams):
        target_sizes[i] += 1

    print(f"[팀 크기 계산] {n_students}명 -> {num_final_teams}개 팀: {dict(Counter(target_sizes))}")

    # --- 2단계: 팀 초기화 및 변수 설정 ---
    teams = [[] for _ in range(num_final_teams)]
    team_leaders_info = [None] * num_final_teams
    assigned_students_ids = set()
    students_list = list(students)

    # --- 3단계: 조장 선정 ---
    print("\n--- 단계 2: 조장 선정 및 우선 배정 ---")
    willing_leaders = sorted([s for s in students_list if s["wants_leader"]], key=lambda x: x["leader_score"], reverse=True)
    non_willing_sorted = sorted([s for s in students_list if not s["wants_leader"]], key=lambda x: x["leader_score"], reverse=True)

    designated_leaders = []
    leader_ids_temp = set()

    for leader in willing_leaders:
        if len(designated_leaders) < num_final_teams:
            designated_leaders.append(leader)
            leader_ids_temp.add(leader["id"])
        else:
            break

    num_needed = num_final_teams - len(designated_leaders)
    if num_needed > 0:
        for student in non_willing_sorted:
            if student["id"] not in leader_ids_temp:
                designated_leaders.append(student)
                leader_ids_temp.add(student["id"])
                if len(designated_leaders) == num_final_teams:
                    break

    for i in range(num_final_teams):
        if i < len(designated_leaders):
            leader = designated_leaders[i]
            teams[i].append({
                **leader,
                "position": leader.get("role", leader.get("position", "")),
            })
            assigned_students_ids.add(leader["id"])
            status = "희망" if leader["wants_leader"] else "비희망"
            team_leaders_info[i] = f"{leader['name']} ({status}, 점수: {leader['leader_score']}) [리더]"
        else:
            team_leaders_info[i] = "N/A [조장 배정 오류]"
            print(f"  경고: Team {i+1} 조장 부족!")

    print("--- 조장 배정 완료 ---")

    # --- 4단계: 나머지 인원 배정 ---
    print("\n--- 단계 3: 나머지 학생 배정 시작 (규칙 기반, 최종 우선순위) ---")
    remaining_students = [s for s in students_list if s["id"] not in assigned_students_ids]
    random.shuffle(remaining_students)

    for student in remaining_students:
        possible_teams_indices = [i for i in range(num_final_teams) if len(teams[i]) < target_sizes[i]]
        if not possible_teams_indices:
            print(f"오류: {student['name']} 배정 팀 없음!")
            continue

        evaluated_teams = []
        for i in possible_teams_indices:
            team = teams[i]
            e_in_team = any(m['ei'] == 'E' for m in team)
            i_in_team = any(m['ei'] == 'I' for m in team)
            fills_ei_need = (not e_in_team and student['ei'] == 'E') or (not i_in_team and student['ei'] == 'I')
            current_temperaments = {m['temperament'] for m in team}
            fills_temperament_need = student['temperament'] not in current_temperaments
            e_count = sum(1 for m in team if m['ei'] == 'E')
            i_count = sum(1 for m in team if m['ei'] == 'I')
            new_e_count = e_count + (1 if student['ei'] == 'E' else 0)
            new_i_count = i_count + (1 if student['ei'] == 'I' else 0)
            ei_diff_after = abs(new_e_count - new_i_count)
            temperament_count_student = sum(1 for m in team if m['temperament'] == student['temperament'])

            evaluated_teams.append({
                'id': i,
                'fills_ei_need': fills_ei_need,
                'fills_temperament_need': fills_temperament_need,
                'ei_diff_after': ei_diff_after,
                'temperament_count_student': temperament_count_student,
                'current_size': len(team)
            })

        evaluated_teams.sort(key=lambda x: (
            x['fills_ei_need'],
            x['fills_temperament_need'],
            -x['ei_diff_after'],
            -x['temperament_count_student'],
            -x['current_size']
        ), reverse=True)

        if evaluated_teams:
            final_team_idx = evaluated_teams[0]['id']
            teams[final_team_idx].append({
                **student,
                "position": student.get("role", student.get("position", "")),
            })
            assigned_students_ids.add(student["id"])
        else:
            print(f"오류: {student['name']} 배정 규칙 적용 실패!")

    print("--- 나머지 학생 배정 완료 ---")

    # ✅ 누락 체크 (id 기준)
    assigned_ids = set()
    for team in teams:
        for m in team:
            assigned_ids.add(m["id"])
    all_ids = set(s["id"] for s in students)
    not_assigned = all_ids - assigned_ids
    if not_assigned:
        print("❗팀에 할당되지 않은 참가자:", not_assigned)
    else:
        print("✅ 모든 참가자가 팀에 배정 완료되었습니다.")

    return teams, team_leaders_info
