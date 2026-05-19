import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./join.css"; // ✅ 네가 제공한 스타일 반영

function JoinRoom() {
  const [roomCode, setRoomCode] = useState("");
  const [password, setPassword] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleJoin = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/join_room/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room_code: roomCode, password })
      });

      const data = await res.json();
      setLoading(false);
      setResponse(data);

      if (res.ok) {
        if (data.is_finalized || data.is_assign_finalized) {
          // ✅ 이미 팀 배정이 완료된 방이라면 바로 팀 결과 페이지로 이동
          navigate(`/teamresult?room=${roomCode}&password=${password}`);
        } else {
          // ✅ 아직 배정 전이면 설문 현황 페이지로
          navigate(`/survey-status?code=${roomCode}&pw=${password}`);
        }
      }
    } catch (err) {
      setLoading(false);
      setResponse({ error: "서버 오류가 발생했습니다." });
    }
  };

  return (
    <div className="create-box">
      <div className="create-form">
        <h2 className="title">방 입장</h2>
        <div className="input-group">
          <input
            type="text"
            placeholder="방 코드 입력"
            value={roomCode}
            onChange={(e) => setRoomCode(e.target.value)}
          />
        </div>
        <div className="input-group">
          <input
            type="password"
            placeholder="비밀번호 입력"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button onClick={handleJoin} className="submit-btn" disabled={loading}>
          {loading ? "확인 중..." : "입장하기"}
        </button>

        {response && response.error && (
          <div style={{ marginTop: 20, color: "red" }}>
            {response.error}
          </div>
        )}
      </div>
    </div>
  );
}

export default JoinRoom;
