import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./result2.css";

// 점수(0~100) → 구간 텍스트 변환 함수
function getScoreLevel(score) {
  score = Number(score);
  if (isNaN(score) || score === null || score === undefined) return null;
  if (score >= 0 && score < 20) return "매우 낮음";
  if (score >= 20 && score < 40) return "낮음";
  if (score >= 40 && score < 50) return "약간 낮음";
  if (score >= 50 && score < 60) return "약간 높음";
  if (score >= 60 && score < 80) return "높음";
  if (score >= 80 && score <= 100) return "매우 높음";
  return null;
}

// MBTI별 설명
const mbtiDescriptions = {
  ISTJ: "체계적이고 신뢰할 수 있어, 팀의 계획 수립과 일정 관리를 책임감 있게 이끈다.",
  ISFJ: "세심하고 조용한 헌신형으로, 팀원들의 필요를 살피며 안정적인 협업 환경을 만든다.",
  INFJ: "팀의 장기적 비전을 명확히 제시하고, 구성원들을 의미 있는 목표로 이끈다.",
  INTJ: "전략적 사고에 능해, 복잡한 문제를 분석하고 미래 지향적인 계획을 수립한다.",
  ISTP: "실용적이고 침착하여 위기 상황에서도 유용한 도구와 해결책을 신속히 제시한다.",
  ISFP: "조용하고 따뜻한 중재자로, 팀 내 갈등을 완화하고 조화로운 분위기를 조성한다.",
  INFP: "이상과 가치를 중시하며, 창의적이고 영감을 주는 아이디어로 팀에 활기를 불어넣는다.",
  INTP: "논리적 분석에 강해, 문제의 핵심을 짚고 독창적인 해결 방안을 제시한다.",
  ESTP: "행동이 빠르고 현실적이어서, 실전 상황에서의 돌파구를 제시하며 팀을 이끈다.",
  ESFP: "유쾌하고 사교적인 분위기 메이커로, 팀원 간 유대를 강화하고 활력을 불어넣는다.",
  ENFP: "열정적이고 창의적인 아이디어 뱅크로, 다양한 가능성을 탐색하며 팀의 역동성을 높인다.",
  ENTP: "도전적이고 혁신적인 사고로, 기존의 방식에 문제를 제기하며 발전 방향을 제시한다.",
  ESTJ: "명확한 목표 설정과 체계적 실행으로, 효율적이고 추진력 있는 팀 운영을 주도한다.",
  ESFJ: "협동과 배려의 중심으로, 팀원들을 세심하게 돌보며 협력적인 분위기를 이끈다.",
  ENFJ: "구성원의 장점을 발견하고 독려하며, 공동 목표를 향해 긍정적 소통을 이끌어낸다.",
  ENTJ: "명확한 비전과 결단력으로 팀을 강하게 리드하며, 도전적 목표 달성을 주도한다."
};

// Big5 설명 텍스트 (개방성-성실성 구간별)
const big5Descriptions = {
  "매우 낮음": {
    "매우 낮음": "새로운 아이디어보다는 익숙한 방식에 익숙하며, 실용적이고 즉흥적인 성향이 강하고 책임감보다는 유연함을 추구합니다.",
    "낮음": "새로운 시도보다는 익숙한 방식을 선호하고, 책임감보다는 자유로움을 중시합니다.",
    "약간 낮음": "아이디어보다 현실을 중시하고, 어느 정도의 책임감과 유연함을 균형 있게 갖추고 있습니다.",
    "약간 높음": "현실적인 감각과 유연성을 모두 갖추고 있습니다.",
    "높음": "기존의 방식을 중시하지만, 주어진 일은 꼼꼼하게 책임집니다.",
    "매우 높음": "현실적이면서도 책임감이 매우 강한 편입니다."
  },
  "낮음": {
    "매우 낮음": "기존 방식을 고수하며, 즉흥적이고 실용적인 면이 두드러집니다.",
    "낮음": "안정적이고 실용적인 방법을 추구하며, 규칙을 중시하지 않을 수 있습니다.",
    "약간 낮음": "현실적이고 실용적인 동시에, 필요할 때 책임감을 보입니다.",
    "약간 높음": "실용성과 책임감을 모두 고려합니다.",
    "높음": "실용성을 바탕으로 일을 체계적으로 해냅니다.",
    "매우 높음": "실용적이고 책임감이 매우 강합니다."
  },
  "약간 낮음": {
    "매우 낮음": "유연하고 실용적이나, 새로운 아이디어 도입에는 소극적입니다.",
    "낮음": "실용성과 자유로움이 조화를 이루며, 필요한 책임감은 갖추고 있습니다.",
    "약간 낮음": "현실적이면서도 기본적인 책임감을 지니고 있습니다.",
    "약간 높음": "필요시 체계적이고 꼼꼼하게 일합니다.",
    "높음": "실용적인 접근과 꼼꼼함이 잘 어우러집니다.",
    "매우 높음": "현실적이면서도 체계적으로 일을 처리합니다."
  },
  "약간 높음": {
    "매우 낮음": "기본적으로 유연하지만 새로운 아이디어 도입은 드문 편입니다.",
    "낮음": "실용성 위주이나 책임감도 어느 정도 보입니다.",
    "약간 낮음": "기본적인 책임감과 유연함을 동시에 갖췄습니다.",
    "약간 높음": "실용성과 체계성을 모두 고려합니다.",
    "높음": "꼼꼼함과 실용성 모두 뛰어납니다.",
    "매우 높음": "실용적이면서도 매우 체계적으로 일합니다."
  },
  "높음": {
    "매우 낮음": "새로운 아이디어에 적극적이면서도 자유로운 스타일을 보입니다.",
    "낮음": "책임감과 유연함을 조화롭게 발휘합니다.",
    "약간 낮음": "유연성과 책임감 모두 우수합니다.",
    "약간 높음": "새로운 접근과 체계적 실행력이 뛰어납니다.",
    "높음": "새로운 아이디어를 책임감 있게 실현하는 타입입니다.",
    "매우 높음": "책임감이 매우 강하면서 창의성도 뛰어납니다."
  },
  "매우 높음": {
    "매우 낮음": "매우 창의적이지만 즉흥적이고 자유로운 경향이 있습니다.",
    "낮음": "창의성과 실용성의 조화를 이루려는 경향이 있습니다.",
    "약간 낮음": "창의성, 실용성, 책임감을 모두 갖추려 노력합니다.",
    "약간 높음": "매우 창의적이면서도 체계적인 사고를 할 수 있습니다.",
    "높음": "매우 창의적이고 책임감도 높아 혁신을 실현할 수 있습니다.",
    "매우 높음": "창의성과 책임감 모두 최고 수준으로, 팀의 혁신과 안정 모두에 크게 기여할 수 있습니다."
  }
};

// Big5와 MBTI 설명 합성 함수
function getCombinedSentence(openness, conscientiousness, mbti) {
  const openLevel = getScoreLevel(openness);
  const consLevel = getScoreLevel(conscientiousness);
  let big5Text = "";
  if (openLevel && consLevel && big5Descriptions[openLevel]?.[consLevel]) {
    big5Text = big5Descriptions[openLevel][consLevel];
  }
  const mbtiText = mbti && mbtiDescriptions[mbti.toUpperCase()]
    ? mbtiDescriptions[mbti.toUpperCase()]
    : "";

  // 자연어 설명 조합
  if (big5Text && mbtiText) return `${big5Text}\n${mbtiText}`;
  if (big5Text) return big5Text;
  if (mbtiText) return mbtiText;
  return "설명 없음";
}

function Result2Page() {
  const location = useLocation();
  const navigate = useNavigate();

  const params = new URLSearchParams(location.search);
  const teamNum = params.get("team") || "";

  // TeamResultPage에서 넘겨주는 멤버 리스트
  const members = location.state?.members || [];

  const [selected, setSelected] = useState(null);

  return (
    <div className="container_b">
      <div className="team-box">
      <h2>{teamNum}조 팀원 명단</h2>
        <ul>
          {members.map((member, idx) => (
            <li key={member.id || idx}>
              <button
                className="member"
                onClick={() => setSelected(member)}
                data-name={member.name}
              >
                {member.name}
                {member.is_leader && (
                  <span className="leader-icon" title="조장">👑</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      </div>
      {/* 멤버 상세 모달 */}
      {selected && (
        <div className="modal" style={{ display: "block" }} onClick={() => setSelected(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <span className="close-btn" onClick={() => setSelected(null)}>
              &times;
            </span>
            <div id="person-name" style={{ fontWeight: 700, fontSize: 22 }}>
              {selected.name}
            </div>
            {/* 자동 설명 생성 */}
            <div id="person-info" style={{ marginTop: 12, marginBottom: 8, whiteSpace: "pre-line" }}>
              {getCombinedSentence(selected.openness, selected.conscientiousness, selected.mbti)}
            </div>
            <div className="member-info">
              <div className="name-line">
                <span style={{ fontWeight: 600 }}>학번:</span>
                <span>{selected.student_id}</span>
              </div>
              <div className="name-line">
                <span style={{ fontWeight: 600 }}>이메일:</span>
                <span className="email">{selected.email}</span>
              </div>
              <div className="name-line">
                <span style={{ fontWeight: 600 }}>연락처:</span>
                <span className="phone">{selected.phone_number}</span>
              </div>
              <div className="name-line">
                <span style={{ fontWeight: 600 }}>포지션:</span>
                <span>{selected.position}</span>
              </div>
              {selected.is_leader && (
                <div style={{ color: "#ff9900", marginTop: 4 }}>조장</div>
              )}
            </div>
          </div>
        </div>
      )}

      <button
        style={{
          marginTop: 28,
          background: "#e5eefd",
          color: "#1976d2",
          fontWeight: 700,
          border: "none",
          borderRadius: 8,
          padding: "10px 24px",
          fontSize: 18,
          cursor: "pointer",
          boxShadow: "0 2px 8px #dae6f7",
        }}
        onClick={() => navigate(-1)}
      >
        뒤로가기
      </button>
    </div>
  );
}

export default Result2Page;
