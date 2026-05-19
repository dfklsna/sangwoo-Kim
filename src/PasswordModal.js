import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function PasswordModal({ closeModal }) {
  const [roomCode, setRoomCode] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!roomCode.trim()) {
      alert("방 코드를 입력하세요.");
      return;
    }
    if (!password.trim()) {
      alert("비밀번호를 입력하세요.");
      return;
    }
    console.log("비밀번호 입력 후 이동!", roomCode, password);
    navigate(`/survey-status?code=${roomCode}&pw=${password}`);
    closeModal();
  };

  return (
    <>
      <div className="modal-box">
        <span className="close-button" onClick={closeModal}>
          &times;
        </span>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="방 코드를 입력하세요"
            value={roomCode}
            onChange={(e) => setRoomCode(e.target.value)}
            autoFocus
          />
          <input
            type="password"
            placeholder="비밀번호를 입력하세요"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">확인</button>
        </form>
      </div>
      <div className="modal-backdrop" onClick={closeModal}></div>
    </>
  );
}

export default PasswordModal;
