import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import "./join.css";

function JoinPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const roomCode = searchParams.get("room");

  // ✅ JoinPage 배경을 퍼즐 11,9,8,10으로 세팅
  useEffect(() => {
    document.body.style.backgroundImage = `
      url('assets/bg-puzzle11.png'),
      url('assets/bg-puzzle9.png'),
      url('assets/bg-puzzle8.png'),
      url('assets/bg-puzzle10.png')
    `;
    document.body.style.backgroundPosition =
      "left top, right top, left bottom, right bottom";
    document.body.style.backgroundRepeat =
      "no-repeat, no-repeat, no-repeat, no-repeat";
    document.body.style.backgroundSize =
      "160px 160px, 160px 160px, 160px 160px, 160px 160px";
    document.body.style.backgroundColor = "#e5f0ff";
    // 나갈 때 메인 배경(1,2,3,4)로 복귀
    return () => {
      document.body.style.backgroundImage = `
        url('assets/bg-puzzle1.png'),
        url('assets/bg-puzzle2.png'),
        url('assets/bg-puzzle3.png'),
        url('assets/bg-puzzle4.png')
      `;
      document.body.style.backgroundPosition =
        "left top, right top, left bottom, right bottom";
      document.body.style.backgroundRepeat =
        "no-repeat, no-repeat, no-repeat, no-repeat";
      document.body.style.backgroundSize =
        "160px 160px, 160px 160px, 160px 160px, 160px 160px";
      document.body.style.backgroundColor = "#e5f0ff";
    };
  }, []);

  const [formData, setFormData] = useState({
    name: "",
    student_id: "",
    phone_number: "",
    email: "",
    leader_preference: "",
    position: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...formData,
      room_code: roomCode,
    };

    try {
      const res = await fetch("http://localhost:8000/api/join_participant/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (!res.ok) {
        alert(data.error || "등록 실패: 유효하지 않은 방 코드입니다.");
        return;
      }

      navigate(`/survey?room=${roomCode}&id=${data.user_id}`);
    } catch (err) {
      alert("서버 오류로 등록에 실패했습니다.");
      console.error(err);
    }
  };

  return (
    <div className="container_a">
      <h2 className="header">팀 참여하기</h2>
      <form className="form" onSubmit={handleSubmit}>
        <div className="input-group">
          <label>이름</label>
          <input
            type="text"
            name="name"
            placeholder="이름을 입력하세요"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>
        <div className="input-group">
          <label>학번</label>
          <input
            type="text"
            name="student_id"
            placeholder="학번을 입력하세요"
            value={formData.student_id}
            onChange={handleChange}
            required
          />
        </div>
        <div className="input-group">
          <label>전화번호</label>
          <input
            type="text"
            name="phone_number"
            placeholder="전화번호를 입력하세요"
            value={formData.phone_number}
            onChange={handleChange}
            required
          />
        </div>
        <div className="input-group">
          <label>이메일</label>
          <input
            type="email"
            name="email"
            placeholder="이메일을 입력하세요"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>
        <div className="radio-group">
          <label>조장 선호 여부</label>
          <div>
            <input
              type="radio"
              name="leader_preference"
              id="yes"
              value="true"
              checked={formData.leader_preference === "true"}
              onChange={handleChange}
              required
            />
            <label htmlFor="yes">예</label>
            <input
              type="radio"
              name="leader_preference"
              id="no"
              value="false"
              checked={formData.leader_preference === "false"}
              onChange={handleChange}
            />
            <label htmlFor="no">아니요</label>
          </div>
        </div>
        <div className="radio-group">
          <label>선호 역할</label>
          <div>
            <input
              type="radio"
              name="position"
              id="back"
              value="backend"
              checked={formData.position === "backend"}
              onChange={handleChange}
              required
            />
            <label htmlFor="back">백엔드</label>
            <input
              type="radio"
              name="position"
              id="front"
              value="frontend"
              checked={formData.position === "frontend"}
              onChange={handleChange}
            />
            <label htmlFor="front">프론트</label>
            <input
              type="radio"
              name="position"
              id="none"
              value="none"
              checked={formData.position === "none"}
              onChange={handleChange}
            />
            <label htmlFor="none">없음</label>
          </div>
        </div>
        <button type="submit" className="submit-btn">
          다음
        </button>
      </form>
      {/* 오른쪽 아래 퍼즐 이미지는 그대로 유지 */}
      <img src="/assets/bg-puzzle1.png" className="puzzle-img" alt="퍼즐 이미지" />
    </div>
  );
}

export default JoinPage;
