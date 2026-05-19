import React, { useState, useEffect } from "react";
import "./survey.css";
import { useNavigate } from "react-router-dom";


function SurveyPage() {
  const navigate = useNavigate();
  const [responses, setResponses] = useState({});
  const [participantId, setParticipantId] = useState(null);

  // URL에서 participant_id 파라미터 추출
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");
    if (id) setParticipantId(parseInt(id));
  }, []);

  // Big Five 질문지 + 메타데이터
  const big5Questions = [
    { text: "나는 상상력이 풍부하다", trait: "openness", reverse: false },
    { text: "나는 예술적 경험을 중요하게 생각한다", trait: "openness", reverse: false },
    { text: "나는 종종 강렬한 감정을 느끼곤 한다", trait: "openness", reverse: false },
    { text: "나는 반복되는 일을 하기 좋아한다", trait: "openness", reverse: true },
    { text: "나는 기발한 사람이며, 깊이 생각한다", trait: "openness", reverse: false },
    { text: "나는 정치적으로 진보적 후보를 뽑는 경향이 있다", trait: "openness", reverse: false },
    { text: "나는 아이디어를 떠올리는 일을 즐긴다", trait: "openness", reverse: false },
    { text: "나는 예술에 대해 거의 관심이 없다", trait: "openness", reverse: true },
    { text: "나는 좀처럼 감정적으로 변하지 않는다", trait: "openness", reverse: true },
    { text: "나는 창의적인 사람이다", trait: "openness", "reverse": false },
    { text: "나는 철학적인 대화를 피하는 편이다", trait: "openness", reverse: true },
    { text: "나는 단 하나의 종교만이 존재한다고 믿는다", trait: "openness", reverse: true },
    { text: "나는 몽상에 빠지는 것을 즐긴다", trait: "openness", reverse: false },
    { text: "나는 미술, 음악, 문학 등에 조예가 깊다", trait: "openness", reverse: false },
    { text: "나는 감정이나 기분에 쉽게 영향을 받지 않는다", trait: "openness", reverse: true },
    { text: "나는 새로운 아이디어를 제시할 수 있다", trait: "openness", reverse: false },
    { text: "나는 추상적 아이디어를 이해하는게 어렵다", trait: "openness", reverse: true },
    { text: "나는 정치적으로 보수적 후보를 뽑는 경향이 있다", trait: "openness", reverse: true },
    { text: "나는 생각에 잠기는 것을 좋아한다", trait: "openness", reverse: false },
    { text: "나는 미술관 가는 것을 즐기지 않는다", trait: "openness", reverse: true },
    { text: "나는 감정 기복이 낮다", trait: "openness", reverse: true },
    { text: "나는 여러 방면에 호기심이 많다", trait: "openness", reverse: false },
    { text: "나는 이론적 이야기를 하는 것에 관심이 없다", trait: "openness", reverse: true },
    { text: "주요 행사 전에 국민의례하는 것을 좋아한다", trait: "openness", reverse: true },
    { text: "나는 독창적인 사람이다", trait: "openness", reverse: false },
    { text: "나는 일을 철두철미하게 해낸다", trait: "conscientiousness", reverse: false },
    { text: "나는 질서정연한 것을 좋아한다", trait: "conscientiousness", reverse: false },
    { text: "나는 약속을 잘 지킨다", trait: "conscientiousness", reverse: false },
    { text: "나는 일을 열심히 한다", trait: "conscientiousness", reverse: false },
    { text: "나는 일을 미루지 않고 바로 시작한다", trait: "conscientiousness", reverse: false },
    { text: "나는 조심성이 없는 편이다", trait: "conscientiousness", reverse: true },
    { text: "나는 일을 효율적으로 하는 사람이다", trait: "conscientiousness", reverse: false },
    { text: "나는 계획을 세우고 그것을 따른다", trait: "conscientiousness", reverse: false },
    { text: "나는 믿을 수 있는 사람이다", trait: "conscientiousness", reverse: false },
    { text: "나는 기대치 이상을 해낸다", trait: "conscientiousness", reverse: false },
    { text: "나는 쉽게 산만해진다", trait: "conscientiousness", reverse: true },
    { text: "나는 무모한 의사 결정을 내리곤 한다", trait: "conscientiousness", reverse: true },
    { text: "나는 일을 능숙하게 처리한다", trait: "conscientiousness", reverse: false },
    { text: "나는 체계적이지 못한 편이다", trait: "conscientiousness", reverse: true },
    { text: "나는 약속을 잘 어긴다", trait: "conscientiousness", reverse: true },
    { text: "나는 스스로와 남들에 대해 높은 기준을 적용한다", trait: "conscientiousness", reverse: false },
    { text: "나는 일을 시작하기 위해 압박이 필요하다", trait: "conscientiousness", reverse: true },
    { text: "나는 급히 일에 뛰어드는 편이다", trait: "conscientiousness", reverse: true },
    { text: "나는 끈기를 갖고 일을 잘 끝낸다", trait: "conscientiousness", reverse: false },
    { text: "나는 내 물건을 어질러 놓곤 한다", trait: "conscientiousness", reverse: true },
    { text: "나는 게으른 편이다", trait: "conscientiousness", reverse: true },
    { text: "나는 성공하고 싶은 욕구가 크지 않다", trait: "conscientiousness", reverse: true },
    { text: "나는 일을 시작하는 데에 어려움을 느낀다", trait: "conscientiousness", reverse: true },
    { text: "나는 생각하지 않고 행동하는 편이다", trait: "conscientiousness", reverse: true },
    { text: "나는 성실한 사람이다", trait: "conscientiousness", reverse: false }
  ];

  const mbtiQuestions = [
  { text: "나는 혼자 있을 때 에너지를 충전한다", trait: "ie", reverse: false },
  { text: "나는 친구들과 어울리는 것을 즐긴다", trait: "ie", reverse: false },
  { text: "나는 내면의 생각에 집중하는 경향이 있다", trait: "ie", reverse: false },
  { text: "나는 외향적으로 보인다는 말을 자주 듣는다", trait: "ie", reverse: false },
  { text: "나는 사교적인 자리를 좋아한다", trait: "ie", reverse: false },

  { text: "나는 현실적인 정보에 의존하는 편이다", trait: "sn", reverse: false },
  { text: "나는 직관적으로 상황을 파악한다", trait: "sn", reverse: true },
  { text: "나는 구체적인 사실을 중시한다", trait: "sn", reverse: false },
  { text: "나는 전체적인 흐름을 중요시한다", trait: "sn", reverse: true },
  { text: "나는 감각을 통해 정보를 얻는 편이다", trait: "sn", reverse: false },

  { text: "나는 결정을 내릴 때 논리와 객관성을 중시한다", trait: "tf", reverse: false },
  { text: "나는 타인의 감정을 고려해 결정을 내린다", trait: "tf", reverse: true },
  { text: "나는 이성적인 사고를 선호한다", trait: "tf", reverse: false },
  { text: "나는 따뜻한 공감을 중요시한다", trait: "tf", reverse: true },
  { text: "나는 문제 해결 시 감정보다는 원칙을 따른다", trait: "tf", reverse: false },

  { text: "나는 계획 세우는 것을 좋아한다", trait: "jp", reverse: false },
  { text: "나는 유연한 일정과 선택을 선호한다", trait: "jp", reverse: true },
  { text: "나는 마감 전에 일을 끝내는 편이다", trait: "jp", reverse: false },
  { text: "나는 즉흥적인 결정을 자주 내린다", trait: "jp", reverse: true },
  { text: "나는 명확한 구조를 선호한다", trait: "jp", reverse: false }
];


  const renderQuestion = (prefix, index, questionText) => {
  const name = `${prefix}${index + 1}`;
  return (
    <div className="question" key={name}>
      <label className="question-text">{`Q${index + 1}. ${questionText}`}</label>
      
      {/* 라디오 버튼 줄 */}
      <div className="options">
        {[0, 1, 2, 3, 4].map((value) => (
          <React.Fragment key={value}>
            <input
              type="radio"
              id={`${name}-${value}`}
              name={name}
              value={value}
              onChange={(e) =>
                setResponses((prev) => ({
                  ...prev,
                  [name]: parseInt(e.target.value),
                }))
              }
            />
            <label
              htmlFor={`${name}-${value}`}
              className={`option-${value + 1}`}
            ></label>
          </React.Fragment>
        ))}
      </div>

    </div>
  );
};




  const average = (arr) =>
    arr.length === 0 ? 0 : arr.reduce((sum, v) => sum + (v ?? 0), 0) / arr.length;

  const inferMBTI = (ie, sn, tf, jp) => {
    const IorE = ie >=10? "E" : "I";
    const SorN = sn >= 10?"S" : "N";
    const TorF = tf >= 10 ? "T" : "F";
    const JorP = jp >= 10 ? "J" : "P";
    return `${IorE}${SorN}${TorF}${JorP}`;
  };

  const handleSubmit = async () => {
    const totalQuestions = big5Questions.length + mbtiQuestions.length;
    const answeredCount = Object.keys(responses).length;

    if (answeredCount < totalQuestions) {
      alert("모든 문항에 응답해주세요!");
      return;
  }
    if (!participantId) {
      alert("참가자 ID가 없습니다. URL을 확인해주세요.");
      return;
    }

    const opennessScores = big5Questions
      .filter((q) => q.trait === "openness")
      .map((q, i) => {
        const val = responses[`big5_q${i + 1}`] ?? 0;
        return q.reverse ? 4 - val : val;
      });

    const conscientiousnessScores = big5Questions
      .filter((q) => q.trait === "conscientiousness")
      .map((q, i) => {
        const offset = big5Questions.findIndex((qq) => qq === q);
        const val = responses[`big5_q${offset + 1}`] ?? 0;
        return q.reverse ? 4 - val : val;
      });

    const mbti = mbtiQuestions.map((q, i) => {
    const val = responses[`mbti_q${i + 1}`] ?? 0;
    return q.reverse ? 4 - val : val;
    });

    const mbti_ie_score = mbti.slice(0, 5).reduce((sum, v) => sum + v, 0);
    const mbti_sn_score = mbti.slice(5, 10).reduce((sum, v) => sum + v, 0);
    const mbti_tf_score = mbti.slice(10, 15).reduce((sum, v) => sum + v, 0);
    const mbti_jp_score = mbti.slice(15, 20).reduce((sum, v) => sum + v, 0);


    const payload = {
      participant_id: participantId,
      openness: opennessScores.reduce((a, b) => a + b, 0),
      conscientiousness: conscientiousnessScores.reduce((a,b)=> a+b, 0),
      mbti_ie_score,
      mbti_sn_score,
      mbti_tf_score,
      mbti_jp_score,
      inferred_mbti: inferMBTI(mbti_ie_score, mbti_sn_score, mbti_tf_score, mbti_jp_score),

    };
    console.log("제출 직전 payload", payload);


    try {
      const res = await fetch("http://localhost:8000/api/submit_survey/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (res.ok) {
        alert("제출 성공: " + JSON.stringify(data));
        navigate("/");

      } else {
        alert("제출 실패: " + JSON.stringify(data));
      }
    } catch (err) {
      alert("제출 중 오류 발생: " + err.message);
    }
  };

  return (
  <div className="survey-container">
    <h1>성격 유형 설문지</h1>

    {/* 👇👇 이 영역만 추가!! 👇👇 */}
    <div className="question-scroll-area">
      <h2>Big Five 성격 설문</h2>
      {big5Questions.map((q, i) => renderQuestion("big5_q", i, q.text))}

      <h2>MBTI 설문</h2>
      {mbtiQuestions.map((q, i) => renderQuestion("mbti_q", i, q.text))}
    </div>
    {/* 👆👆 이 영역만 추가!! 👆👆 */}

    <button type="button" className="submit-btn" onClick={handleSubmit}>
      제출하기
    </button>
  </div>
);

}

export default SurveyPage;

