import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./create.css";

function CreateTeam() {
  const [type, setType] = useState("");
  const [total, setTotal] = useState("");
  const [mode, setMode] = useState("");
  const [count, setCount] = useState("");
  const [people, setPeople] = useState("");

  const navigate = useNavigate();

  // 퍼즐 배경 적용
  useEffect(() => {
    const style = document.createElement("style");
    style.innerHTML = `
      body {
        background-color: #e5f0ff;
        background-image:
          url(${process.env.PUBLIC_URL}/assets/bg-puzzle11.png),
          url(${process.env.PUBLIC_URL}/assets/bg-puzzle9.png),
          url(${process.env.PUBLIC_URL}/assets/bg-puzzle8.png),
          url(${process.env.PUBLIC_URL}/assets/bg-puzzle10.png);
        background-repeat: no-repeat;
        background-size: 160px 160px, 160px 160px, 160px 160px, 160px 160px;
        background-position:
          left top,
          right top,
          left bottom,
          right bottom;
      }
    `;
    document.head.appendChild(style);
    return () => {
      document.head.removeChild(style);
    };
  }, []);

  const goHome = () => {
    navigate("/");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const totalInt = parseInt(total, 10);
    const countInt = parseInt(count, 10);
    const peopleInt = parseInt(people, 10);

    if (isNaN(totalInt) || totalInt <= 0) {
      alert("인원 수를 올바르게 입력하세요.");
      return;
    }

    let payload = {
      total_members: totalInt,
      team_type: type === "dev" ? "development" : "non-development",
      division_type: mode === "count" ? "BY_TEAM_COUNT" : "BY_MEMBER_COUNT",
    };

    if (mode === "count") {
      if (isNaN(countInt) || countInt <= 0) {
        alert("조 갯수를 올바르게 입력하세요.");
        return;
      }
      if (countInt > totalInt) {
        alert("조의 갯수는 전체 인원 수보다 많을 수 없습니다.");
        return;
      }
      payload.total_teams = countInt;
    } else if (mode === "people") {
      if (isNaN(peopleInt) || peopleInt <= 0) {
        alert("조 인원 수를 올바르게 입력하세요.");
        return;
      }
      if (peopleInt > totalInt) {
        alert("조 인원 수는 전체 인원 수보다 많을 수 없습니다.");
        return;
      }
      payload.max_members = peopleInt;
    }

    try {
      const res = await fetch("http://localhost:8000/api/create_team/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error("조 생성 실패");

      localStorage.setItem("room_code", data.room_code);
      localStorage.setItem("room_password", data.password);

      navigate(`/success?room=${data.room_code}&pw=${data.password}`);
    } catch (err) {
      alert("조 생성에 실패했습니다. " + err.message);
    }
  };

  return (
    <section className="create-box">
      <div className="create-header">
        <button className="back-button" onClick={goHome}>←</button>
        <span className="title">조 생성</span>
      </div>

      <form className="create-form" onSubmit={handleSubmit}>
        <div className="radio-group">
          <span className="group-title">조 생성</span>
          <div className="radio-set">
            <label>
              <input
                type="radio"
                name="type"
                value="dev"
                checked={type === "dev"}
                onChange={() => setType("dev")}
                required
              />
              개발
            </label>
            <label>
              <input
                type="radio"
                name="type"
                value="general"
                checked={type === "general"}
                onChange={() => setType("general")}
              />
              일반
            </label>
          </div>
        </div>

        {/* 인원 수: 라디오 없이 왼쪽 딱 붙임 */}
        <div className="input-row">
          <label htmlFor="total">인원 수</label>
          <input
            type="number"
            id="total"
            name="total"
            value={total}
            onChange={(e) => setTotal(e.target.value)}
            required
          />
        </div>

        {/* 조 갯수: 라디오 + 라벨 + input */}
        <div className="input-row">
          <input
            type="radio"
            name="mode"
            value="count"
            checked={mode === "count"}
            onChange={() => setMode("count")}
            required
            id="radio-count"
          />
          <label htmlFor="count" style={{ marginLeft: "8px" }}>조 갯수</label>
          <input
            type="number"
            id="count"
            name="count"
            value={count}
            onChange={(e) => setCount(e.target.value)}
            disabled={mode !== "count"}
          />
        </div>

        {/* 조 인원 수: 라디오 + 라벨 + input */}
        <div className="input-row">
          <input
            type="radio"
            name="mode"
            value="people"
            checked={mode === "people"}
            onChange={() => setMode("people")}
            id="radio-people"
          />
          <label htmlFor="people" style={{ marginLeft: "8px" }}>조 인원 수</label>
          <input
            type="number"
            id="people"
            name="people"
            value={people}
            onChange={(e) => setPeople(e.target.value)}
            disabled={mode !== "people"}
          />
        </div>

        <button type="submit" className="submit-btn">
          생성하기
        </button>
      </form>
    </section>
  );
}

export default CreateTeam;
