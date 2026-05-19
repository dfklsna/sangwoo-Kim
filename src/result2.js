const members = document.querySelectorAll('.member');
const modal = document.getElementById('modal');
const personName = document.getElementById('person-name');
const personInfo = document.getElementById('person-info');
const closeBtn = document.getElementById('closeBtn');

// 인물 설명 사전
const infoMap = {
  '백하린': '2조의 조장으로 책임감 있고 협업 능력이 뛰어납니다.',
  '박지후': '분위기 메이커로 팀에 활기를 불어넣습니다.',
  '김상우': '기획과 문서 작업에 강한 성실한 팀원입니다.',
  '윤지호': '기술적인 지식이 풍부하여 개발에 큰 기여를 합니다.'
};

members.forEach(member => {
  member.addEventListener('click', () => {
    const name = member.dataset.name;
    personName.textContent = name;
    personInfo.textContent = infoMap[name] || '아직 등록된 설명이 없습니다.';
    modal.style.display = 'block';
  });
});

closeBtn.addEventListener('click', () => {
  modal.style.display = 'none';
});

window.addEventListener('click', e => {
  if (e.target === modal) {
    modal.style.display = 'none';
  }
});
