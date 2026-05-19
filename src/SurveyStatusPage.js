import React, { useEffect, useState } from "react";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from "chart.js";
import { useNavigate } from "react-router-dom";

ChartJS.register(ArcElement, Tooltip, Legend);

function SurveyStatusPage() {
  const params = new URLSearchParams(window.location.search);
  const roomCode = params.get("code");
  const password = params.get("pw");

  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!roomCode || !password) {
      setStatus({ error: "방 코드 또는 비밀번호가 없습니다." });
      setLoading(false);
      return;
    }
    fetch("/api/survey_status/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ room_code: roomCode, password: password }),
    })
      .then(res => res.json())
      .then(data => {
        console.log("[survey_status 응답]", data); // ✅ 응답 콘솔에 찍기
        // ✅ 조 편성 완료된 방이면 결과 페이지로 이동!
        if (data.is_assign_finalized) {
          navigate(`/teamresult?room=${roomCode}&password=${password}`);
          return;
        }
        setStatus(data);
        setLoading(false);
      })
      .catch(err => {
        setStatus({ error: "설문 현황을 불러오지 못했습니다." });
        setLoading(false);
      });
  }, [roomCode, password, navigate]);

  let total_members = status?.total_members || 0;
  let responded = status?.responded || 0;
  let notResponded = Math.max(0, total_members - responded);

  const pieData = {
    labels: ["응답", "미응답"],
    datasets: [
      {
        data: [responded, notResponded],
        backgroundColor: ["#4f80ff", "#e5e7eb"]
      }
    ]
  };

  const isComplete = total_members > 0 && responded === total_members;

  // 팀 배정 버튼 클릭
  const handleCreate = () => {
    if (!isComplete) {
      alert("모든 참가자가 설문을 완료해야 실행할 수 있습니다.");
      return;
    }
    fetch("/api/team_assign/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ room_code: roomCode, password: password }),
    })
      .then(res => res.json())
      .then(data => {
        if (data && !data.error) {
          alert("팀 배정이 완료되었습니다!");
          // ✅ 팀 결과 페이지로 이동!
          navigate(`/teamresult?room=${roomCode}&password=${password}`);
        } else {
          alert(data.error || "팀 배정 실패");
        }
      })
      .catch(() => {
        alert("팀 배정 중 오류가 발생했습니다.");
      });
  };

  if (loading) return <div>로딩 중...</div>;
  if (!status || status.error) {
    return <div style={{ color: "red" }}>오류: {status?.error || "설문 현황 없음"}</div>;
  }

  return (
    <div
      style={{
        width: "100vw",
        minHeight: "100vh",
        background: "#f2f6fe",
        display: "flex",
        alignItems: "center",
        justifyContent: "center"
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          gap: "48px",
          padding: "40px",
          borderRadius: "18px",
          background: "#fff",
          boxShadow: "0 2px 16px #c7dbff50"
        }}
      >
        {/* 왼쪽: 파이차트+중앙 텍스트 */}
        <div
          style={{
            width: 260,
            height: 260,
            background: "transparent",
            position: "relative",
            display: "flex",
            alignItems: "center",
            justifyContent: "center"
          }}
        >
          <Pie
            data={pieData}
            options={{
              plugins: {
                legend: { display: false },
                tooltip: { enabled: true }
              },
              cutout: "75%"
            }}
            width={260}
            height={260}
          />
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              transform: "translate(-50%, -50%)",
              textAlign: "center",
              pointerEvents: "none",
              userSelect: "none",
              color: "#4f80ff"
            }}
          >
            <div style={{ fontSize: 28, fontWeight: 600 }}>
              {responded} / {total_members}
            </div>
            <div style={{ fontSize: 18 }}>
              {total_members === 0 ? 0 : Math.round((responded / total_members) * 100)}%
            </div>
          </div>
        </div>

        {/* 오른쪽: 흰색 info box */}
        <div
          style={{
            background: "#f7f9fc",
            borderRadius: "14px",
            minWidth: 220,
            padding: "30px 30px 22px 30px",
            boxShadow: "0 1px 6px #c7dbff40",
            display: "flex",
            flexDirection: "column",
            alignItems: "center"
          }}
        >
          <div style={{ fontWeight: 700, fontSize: 18, marginBottom: 16 }}>설문 완료자 명단</div>
          <div style={{
            minHeight: 100,
            marginBottom: 24,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            color: "#222"
          }}>
            {Array.isArray(status.submitted) && status.submitted.length === 0
              ? <div>설문 완료자 없음</div>
              : status.submitted.map(name => <div key={name}>{name}</div>)
            }
          </div>
          <button
            style={{
              marginTop: 6,
              padding: "10px 22px",
              borderRadius: "8px",
              border: "none",
              background: "#4f80ff",
              color: "#fff",
              fontWeight: 700,
              fontSize: 15,
              letterSpacing: "0.01em",
              cursor: "pointer",
              boxShadow: "0 2px 10px #c7dbff40"
            }}
            onClick={handleCreate}
          >
            생성하기
          </button>
        </div>
      </div>
    </div>
  );
}

export default SurveyStatusPage;
