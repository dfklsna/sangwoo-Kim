// src/Home.js
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./home.css";
import PasswordModal from "./PasswordModal";

function Home() {
  const navigate = useNavigate();
  // 참가 모달(방 코드 입력)용 state
  const [roomCode, setRoomCode] = useState("");
  const [showRoomModal, setShowRoomModal] = useState(false);
  // 조 목록(설문 현황) 모달
  const [showPasswordModal, setShowPasswordModal] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/test/")
      .then((res) => res.json())
      .then((data) => console.log("✅ 백엔드 응답:", data))
      .catch((err) => console.error("❌ 백엔드 연결 실패:", err));
  }, []);

  const goCreate = () => navigate("/create");
  const startListFlow = () => setShowPasswordModal(true);
  const startJoinFlow = () => setShowRoomModal(true);

  // 모달 닫기 (둘 다)
  const closeModal = () => {
    setRoomCode(""); // 참가 모달 초기화
    setShowRoomModal(false);
    setShowPasswordModal(false);
  };

  // 참가 모달 - 방코드 제출
  const submitRoomCode = async () => {
    if (!roomCode.trim()) {
      alert("방 코드를 입력해주세요.");
      return;
    }
    try {
      const res = await fetch("/api/join_room/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room_code: roomCode }),
      });

      if (!res.ok) {
        const data = await res.json();
        alert(data.error || "존재하지 않는 방 코드입니다.");
        return;
      }

      navigate(`/join?room=${roomCode}`);
      closeModal();
    } catch (err) {
      alert("서버 오류가 발생했습니다.");
    }
  };

  return (
    <div>
      {/* ✅ 퍼즐 배경 */}
      <img src="assets/bg-puzzle1.png" className="bg-puzzle puzzle-1" alt="" />
      <img src="assets/bg-puzzle2.png" className="bg-puzzle puzzle-2" alt="" />
      <img src="assets/bg-puzzle3.png" className="bg-puzzle puzzle-3" alt="" />
      <img src="assets/bg-puzzle4.png" className="bg-puzzle puzzle-4" alt="" />

      {/* ✅ 로고 */}
      <h1 className="logo">Teametry</h1>

      {/* ✅ 퍼즐 버튼 */}
      <div className="button-group">
        <div className="puzzle-button" onClick={goCreate}>
          <img src="assets/create.svg" alt="조 생성" />
        </div>
        <div className="puzzle-button" onClick={startListFlow}>
          <img src="assets/list.svg" alt="조 목록" />
        </div>
        <div className="puzzle-button" onClick={startJoinFlow}>
          <img src="assets/join.svg" alt="참가" />
        </div>
      </div>

      {/* ✅ 참가(방코드) 입력 모달 */}
      {showRoomModal && (
        <>
          <div className="modal-box">
            <span className="close-button" onClick={closeModal}>
              &times;
            </span>
            <input
              type="text"
              placeholder="방 코드를 입력하세요"
              value={roomCode}
              onChange={(e) => setRoomCode(e.target.value)}
              autoFocus
            />
            <button onClick={submitRoomCode}>확인</button>
          </div>
          <div className="modal-backdrop" onClick={closeModal}></div>
        </>
      )}

      {/* ✅ 조 목록(설문 현황) 모달 (방코드+비번) */}
      {showPasswordModal && (
        <PasswordModal closeModal={closeModal} />
      )}
    </div>
  );
}

export default Home;







