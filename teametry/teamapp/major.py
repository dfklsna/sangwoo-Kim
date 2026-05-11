import math
import random
from collections import Counter

def assign_developer_teams_final_logic(students, division_type, max_members=None, total_teams=None):
    n_students = len(students)
    if n_students == 0: return [], []

    # --- 팀 수 계산 ---
    if division_type == "BY_MEMBER_COUNT":
        if max_members is None:
            raise ValueError("BY_MEMBER_COUNT requires max_members")
        num_final_teams = math.ceil(n_students / max_members)
    elif division_type == "BY_TEAM_COUNT":
        if total_teams is None:
            raise ValueError("BY_TEAM_COUNT requires total_teams")
        num_final_teams = total_teams
    else:
        raise ValueError("Invalid division_type")

    base_size = n_students // num_final_teams
    target_sizes = [base_size] * num_final_teams
    for i in range(n_students % num_final_teams):
        target_sizes[i] += 1

    teams = [[] for _ in range(num_final_teams)]
    team_leaders_info = [None] * num_final_teams
    assigned_students_ids = set()
    students_list_original = list(students)

    # --- 리더 선정 로직 ---
    willing_leaders = sorted(
        [s for s in students_list_original if s["wants_leader"]],
        key=lambda x: x["leader_score"],
        reverse=True
    )
    non_willing = sorted(
        [s for s in students_list_original if not s["wants_leader"]],
        key=lambda x: x["leader_score"],
        reverse=True
    )

    designated_leaders = []
    used_ids = set()

    for leader in willing_leaders:
        if len(designated_leaders) == num_final_teams:
            break
        designated_leaders.append(leader)
        used_ids.add(leader["id"])

    for backup in non_willing:
        if len(designated_leaders) == num_final_teams:
            break
        if backup["id"] not in used_ids:
            designated_leaders.append(backup)
            used_ids.add(backup["id"])

    if len(designated_leaders) < num_final_teams:
        raise ValueError(f"리더 수 부족: {len(designated_leaders)}명만 확보됨")

    for i in range(num_final_teams):
        leader = designated_leaders[i]
        leader["is_leader"] = True  # CSV 저장 시 일관되게 활용
        teams[i].append({
            **leader,
            "position": leader.get("role", leader.get("position", "")),  # ✅ 항상 position도 추가
        })
        assigned_students_ids.add(leader["id"])
        team_leaders_info[i] = leader["name"]

    # --- 나머지 학생 배정 (역할 -> E/I -> 기질) ---
    remaining_students = [s for s in students_list_original if s["id"] not in assigned_students_ids]
    random.shuffle(remaining_students)

    for student in remaining_students:
        student["is_leader"] = False  # 명시적으로 추가
        possible_teams = [i for i in range(num_final_teams) if len(teams[i]) < target_sizes[i]]
        if not possible_teams:
            raise Exception(f"배정 불가: {student['name']}({student['id']}) -- 팀별 현재 인원: {[len(t) for t in teams]}, 목표: {target_sizes}")

        evaluations = []
        for i in possible_teams:
            team = teams[i]
            be = sum(1 for m in team if m.get("role") == "백엔드" or m.get("position") == "백엔드")
            fe = sum(1 for m in team if m.get("role") == "프론트엔드" or m.get("position") == "프론트엔드")
            new_be = be + (student.get("role") == "백엔드" or student.get("position") == "백엔드")
            new_fe = fe + (student.get("role") == "프론트엔드" or student.get("position") == "프론트엔드")
            role_diff = abs(new_be - new_fe)
            improves_balance = role_diff < abs(be - fe)
            fills_role_gap = (student.get("role") == "백엔드" and be == 0) or (student.get("role") == "프론트엔드" and fe == 0)

            e = sum(1 for m in team if m["ei"] == "E")
            i_ = sum(1 for m in team if m["ei"] == "I")
            new_e = e + (student["ei"] == "E")
            new_i = i_ + (student["ei"] == "I")
            ei_diff = abs(new_e - new_i)
            fills_ei_gap = (e == 0 and student["ei"] == "E") or (i_ == 0 and student["ei"] == "I")

            temp_set = set(m["temperament"] for m in team)
            fills_temp_gap = student["temperament"] not in temp_set
            temp_dup_count = sum(1 for m in team if m["temperament"] == student["temperament"])

            evaluations.append({
                "id": i,
                "fills_role_gap": fills_role_gap,
                "improves_balance": improves_balance,
                "role_diff": role_diff,
                "fills_ei_gap": fills_ei_gap,
                "ei_diff": ei_diff,
                "fills_temp_gap": fills_temp_gap,
                "temp_dup_count": temp_dup_count,
                "team_size": len(team)
            })

        evaluations.sort(key=lambda x: (
            x["fills_role_gap"],
            x["improves_balance"],
            -x["role_diff"],
            x["fills_ei_gap"],
            -x["ei_diff"],
            x["fills_temp_gap"],
            -x["temp_dup_count"],
            -x["team_size"]
        ), reverse=True)

        best_team_idx = evaluations[0]["id"]
        teams[best_team_idx].append({
            **student,
            "position": student.get("role", student.get("position", "")),  # ✅ 항상 position도 추가
        })
        assigned_students_ids.add(student["id"])

    # --- 누락 체크 ---
    assigned_ids = set()
    for team in teams:
        for m in team:
            assigned_ids.add(m["id"])
    all_ids = set(s["id"] for s in students)
    not_assigned = all_ids - assigned_ids
    if not_assigned:
        print(f"❗팀에 할당되지 않은 참가자: {not_assigned}")
        for s in students:
            if s["id"] in not_assigned:
                print("누락자 정보:", s)
    else:
        print("✅ 모든 참가자가 팀에 배정 완료되었습니다.")

    return teams, team_leaders_info

