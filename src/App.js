// src/App.js
import React from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./Home";
import CreateTeam from "./CreateTeam";
import SuccessPage from "./SuccessPage";
import JoinPage from "./JoinPage";
import SurveyPage from "./SurveyPage";
import SurveyStatusPage from "./SurveyStatusPage";  // 설문 현황
import TeamResultPage from "./TeamResultPage";      // 팀 결과
import Result2Page from "./Result2Page";            // 추가!

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/create" element={<CreateTeam />} />
      <Route path="/success" element={<SuccessPage />} />
      <Route path="/join" element={<JoinPage />} />
      <Route path="/survey" element={<SurveyPage />} />
      <Route path="/survey-status" element={<SurveyStatusPage />} />
      <Route path="/teamresult" element={<TeamResultPage />} />
      <Route path="/result2" element={<Result2Page />} /> {/* result2 라우트 추가! */}
    </Routes>
  );
}

export default App;








