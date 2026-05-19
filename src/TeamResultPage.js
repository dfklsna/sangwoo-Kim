import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./result.css";

function TeamResultPage() {
  const [teams, setTeams] = useState({});
  const [isFinalized, setIsFinalized] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null); // {teamNum, idx, memberId}

  const location = useLocation();
  const navigate = useNavigate();
  const params = new URLSearchParams(location.search);
  const roomCode = params.get("room");
  const password = params.get("password");

  useEffect(() => {
    if (!roomCode || !password) {
      alert("잘못된 접근입니다.");
      navigate("/");
      return;
    }
    fetch("http://localhost:8000/api/team_result/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ room_code: roomCode, password }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.teams) {
          const teamNums = Object.keys(data.teams);
          const normalizedTeams =
            teamNums.length > 0
              ? teamNums.reduce((acc, num) => {
                  acc[num] = data.teams[num] || [];
                  return acc;
                }, {})
              : { "1": [] };
          setTeams(normalizedTeams);
          setIsFinalized(data.is_finalized || false);
        } else if (data.error) {
          alert(data.error || "결과 조회 실패");
        }
        setLoading(false);
      });
  }, [roomCode, password, navigate]);

  // 중복 id 체크 + 구조 로그
  useEffect(() => {
    const allIds = Object.values(teams)
      .flat()
      .map((m) => m.id);
    const duplicates = allIds.filter(
      (id, idx, arr) => arr.indexOf(id) !== idx
    );
    if (duplicates.length > 0) {
      console.error("🚨 [팀 내 id 중복 발생!] 중복 id:", duplicates);
    } else {
      console.log("✅ 팀 내 id 중복 없음");
    }
    console.log("🗂️ [teams 구조]:", JSON.stringify(teams));
    Object.entries(teams).forEach(([teamNum, members]) => {
      console.log(
        `[${teamNum}조] 멤버 id 리스트:`,
        members.map((m) => m.id)
      );
    });
  }, [teams]);

  // 조장 지정
  const toggleLeader = (teamNum, memberIdx) => {
    if (isFinalized) return;
    setTeams((prev) => {
      const updated = { ...prev };
      updated[teamNum] = updated[teamNum].map((m, i) => ({
        ...m,
        is_leader: i === memberIdx ? !m.is_leader : false,
      }));
      return updated;
    });
  };

  // 멤버 선택 (조 내 단일 선택)
  const handleMemberClick = (teamNum, idx, memberId) => {
    if (isFinalized) return;
    if (selected && selected.teamNum === teamNum && selected.idx === idx) {
      setSelected(null); // 같은 상자 클릭 시 해제
    } else {
      setSelected({ teamNum, idx, memberId });
    }
  };

  // 조 이동 (선택된 멤버를 targetTeamNum으로 이동)
  const handleMove = (targetTeamNum) => {
    if (!selected) return;
    setTeams((prev) => {
      // 원래 조에서 멤버 제거
      const member = prev[selected.teamNum][selected.idx];
      const newPrev = { ...prev };
      newPrev[selected.teamNum] = prev[selected.teamNum].filter(
        (_, i) => i !== selected.idx
      );
      // 대상 조에 추가 (맨 끝에)
      newPrev[targetTeamNum] = [...prev[targetTeamNum], member];
      return newPrev;
    });
    setSelected(null); // 선택 해제
  };

  const handleSave = async () => {
    const apiTeams = {};
    Object.entries(teams).forEach(([teamNum, members]) => {
      apiTeams[teamNum] = members.map((m) => ({
        participant_id: m.id,
        position: m.position,
        is_leader: !!m.is_leader,
      }));
    });
    const payload = {
      room_code: roomCode,
      password,
      teams: apiTeams,
      finalize: false,
    };
    const res = await fetch("/api/change_team_assignment/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (res.ok) alert("저장 성공");
    else alert(data.error || "저장 실패");
  };

  const handleFinalize = async () => {
    if (
      !window.confirm(
        "정말 최종 확정하시겠습니까? 확정 후에는 수정 불가합니다."
      )
    )
      return;
    const apiTeams = {};
    Object.entries(teams).forEach(([teamNum, members]) => {
      apiTeams[teamNum] = members.map((m) => ({
        participant_id: m.id,
        position: m.position,
        is_leader: !!m.is_leader,
      }));
    });
    const payload = {
      room_code: roomCode,
      password,
      teams: apiTeams,
      finalize: true,
    };
    const res = await fetch("/api/change_team_assignment/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (res.ok) {
      alert("최종 확정되었습니다!");
      setIsFinalized(true);
    } else {
      alert(data.error || "최종 확정 실패");
    }
  };

  if (loading || Object.keys(teams).length === 0) {
    return <div>불러오는 중...</div>;
  }

  // 선택된 멤버 정보
  const selectedInfo = selected
    ? {
        teamNum: selected.teamNum,
        idx: selected.idx,
        member: teams[selected.teamNum]?.[selected.idx],
      }
    : null;

  // 👇 result2로 이동할 때 조원 명단만 props로 전달
  const goToTeamDetail = (teamNum) => {
    const teamMembers = teams[teamNum] || [];
    navigate(`/result2?room=${roomCode}&team=${teamNum}`, { state: { members: teamMembers } });
  };

  // 홈으로 이동
  const goHome = () => {
    navigate("/");
  };

  // 리더점수 계산 함수 (혹시 값이 undefined/null일 때 0 처리)
  const getLeaderScore = (member) => {
    const open = Number(member.openness) || 0;
    const cons = Number(member.conscientiousness) || 0;
    return open + cons;
  };

  return (
    <div className="container">
      <h2>팀 편성 결과 (선택 후 조 이동 가능)</h2>
      <button onClick={goHome} style={{
        marginBottom: "24px",
        background: "#e5eefd",
        color: "#1976d2",
        fontWeight: 700,
        border: "none",
        borderRadius: 8,
        padding: "10px 24px",
        fontSize: 18,
        cursor: "pointer",
        boxShadow: "0 2px 8px #dae6f7",
      }}>
        홈으로
      </button>
      <div className="team-board">
        {Object.entries(teams).map(([teamNum, members]) => (
          <div className="team-column" key={teamNum} style={{ marginBottom: 24 }}>
            <h3>{teamNum}조</h3>
            <div style={{ fontSize: 10, color: "gray" }}>
              ids: [{members.map((m) => m.id).join(", ")}]
            </div>
            {members.map((member, idx) => {
              const isSelected =
                selected &&
                selected.teamNum === teamNum &&
                selected.idx === idx;
              return (
                <div
                  className="member"
                  key={member.id}
                  style={{
                    background: isSelected ? "#cde6fe" : "#fff",
                    border: isSelected
                      ? "2.5px solid #1976d2"
                      : "1px solid #e0e7ff",
                    borderRadius: 7,
                    marginBottom: 10,
                    padding: "10px 12px",
                    cursor: isFinalized ? "not-allowed" : "pointer",
                  }}
                  onClick={() => handleMemberClick(teamNum, idx, member.id)}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <b>{member.name}</b>
                    <span>
                      <button
                        style={{
                          fontSize: 12,
                          color: member.is_leader ? "#1976d2" : "#bbb",
                          border: "none",
                          background: "none",
                          cursor: isFinalized ? "not-allowed" : "pointer",
                        }}
                        disabled={isFinalized}
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleLeader(teamNum, idx);
                        }}
                        title="조장 지정"
                      >
                        [조장]
                      </button>
                    </span>
                  </div>
                  <div>
                    {member.position !== "none" && <>({member.position})</>}
                  </div>
                  <div style={{ fontSize: "12px", color: "#8898b3" }}>
                    학번: {member.student_id}
                  </div>
                  <div style={{ fontSize: "12px", color: "#8898b3" }}>
                    {member.email}
                  </div>
                  <div style={{ fontSize: "12px", color: "#8898b3" }}>
                    {member.phone_number}
                  </div>
                  {/* ⭐️ 리더점수 표시 부분 ⭐️ */}
                  <div style={{ fontSize: "12px", color: "#fa991c" }}>
                    리더점수: {getLeaderScore(member)}점
                  </div>
                </div>
              );
            })}
            {/* 👇 조원 보기(result2로 이동) 버튼 추가 */}
            <div style={{ marginTop: 14, textAlign: "center" }}>
              <button
                onClick={() => goToTeamDetail(teamNum)}
                style={{
                  background: "#1976d2",
                  color: "#fff",
                  fontWeight: 600,
                  border: "none",
                  borderRadius: 8,
                  padding: "9px 24px",
                  fontSize: 16,
                  boxShadow: "0 2px 8px #dae6f7",
                  cursor: "pointer",
                }}
              >
                {teamNum}조 보기
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* 선택된 멤버가 있으면 조 이동 버튼들 생성 */}
      {selectedInfo && (
        <div style={{ margin: "32px 0 12px 0", textAlign: "center" }}>
          <div style={{ marginBottom: 10, color: "#1976d2" }}>
            <b>
              [{selectedInfo.member?.name}] 님을 다른 조로 이동:
            </b>
          </div>
          {Object.keys(teams)
            .filter((num) => num !== selectedInfo.teamNum)
            .map((num) => (
              <button
                key={num}
                onClick={() => handleMove(num)}
                style={{
                  margin: "0 12px",
                  background: "#1976d2",
                  color: "#fff",
                  fontWeight: 600,
                  border: "none",
                  borderRadius: 8,
                  padding: "8px 20px",
                  fontSize: 16,
                  boxShadow: "0 2px 8px #dae6f7",
                  cursor: "pointer",
                }}
              >
                {num}조로 이동
              </button>
            ))}
        </div>
      )}

      {/* 저장/완료 버튼 */}
      <div style={{ marginTop: "24px", textAlign: "center" }}>
        <button
          onClick={handleSave}
          disabled={isFinalized}
          style={{ marginRight: 12 }}
        >
          저장
        </button>
        <button onClick={handleFinalize} disabled={isFinalized}>
          완료
        </button>
        {isFinalized && (
          <div
            style={{ marginTop: 8, color: "#2b7a2b", fontWeight: 700 }}
          >
            ✅ 팀 배정이 최종 확정되어 더이상 수정할 수 없습니다.
          </div>
        )}
      </div>
    </div>
  );
}

export default TeamResultPage;
