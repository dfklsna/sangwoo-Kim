import React, { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import './style2.css';

function SuccessPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const room = searchParams.get("room");
  const pw = searchParams.get("pw");

  const [link, setLink] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!room || !pw) {
      setError("방 정보가 유효하지 않습니다.");
      return;
    }

    fetch(`http://localhost:8000/api/rooms/${room}/info?pw=${encodeURIComponent(pw)}`)
      .then((res) => {
        if (!res.ok) throw new Error("정보 불러오기 실패");
        return res.json();
      })
      .then((data) => {
        setLink(data.link);
      })
      .catch(() => {
        setError("팀 정보를 불러오는 데 실패했습니다.");
      });
  }, [room, pw]);

  const copy = (text) => {
    navigator.clipboard.writeText(text);
    alert("복사되었습니다: " + text);
  };

  if (error) {
    return <div className="success-container"><p>{error}</p></div>;
  }

  return (
    <div className="success-container">
      <div className="success-box">
        <div className="message">팀이 성공적으로 생성되었습니다!</div>

        <div className="field">
          <label>방 코드</label>
          <div className="copy-box">
            <input value={room || ""} readOnly />
            <button onClick={() => copy(room)}>복사</button>
          </div>
        </div>

        <div className="field">
          <label>비밀번호</label>
          <div className="copy-box">
            <input value={pw || ""} readOnly />
            <button onClick={() => copy(pw)}>복사</button>
          </div>
        </div>

        <div className="field">
          <label>링크</label>
          <div className="copy-box">
            <input value={link || ""} readOnly />
            <button onClick={() => copy(link)}>복사</button>
          </div>
        </div>

        <button className="home-btn" onClick={() => navigate("/")}>홈으로</button>
      </div>
    </div>
  );
}

export default SuccessPage;

