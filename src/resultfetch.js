// resultfetch.js

document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/teams") // 🔁 실제 API 주소로 수정 필요
        .then((res) => {
            if (!res.ok) throw new Error("데이터 불러오기 실패");
            return res.json();
        })
        .then((teams) => {
            const board = document.getElementById("team-board");

            teams.forEach((team, index) => {
                const teamDiv = document.createElement("div");
                teamDiv.className = "team-column";
                teamDiv.id = `team-${index + 1}`;

                // 팀 제목
                const title = document.createElement("h3");
                title.innerText = `${team.teamName} (성향점수)`;
                teamDiv.appendChild(title);

                // 조장 표시
                const leaderDiv = document.createElement("div");
                leaderDiv.className = "member";
                leaderDiv.draggable = true;
                leaderDiv.innerHTML = `<strong>조장</strong><br />
          이름: ${team.leader.name}<br />
          전화번호: ${team.leader.phone}<br />
          이메일: ${team.leader.email}<br />
          점수: ${team.leader.score}`;
                teamDiv.appendChild(leaderDiv);

                // 일반 팀원들
                team.members.forEach((member) => {
                    const memberDiv = document.createElement("div");
                    memberDiv.className = "member";
                    memberDiv.draggable = true;
                    memberDiv.innerHTML = `이름: ${member.name}<br />
            전화번호: ${member.phone}<br />
            이메일: ${member.email}<br />
            점수: ${member.score}`;
                    teamDiv.appendChild(memberDiv);
                });

                // result2 링크 (옵션)
                const link = document.createElement("a");
                link.href = "result2.html";
                link.className = "team-link";
                link.innerText = "👉 result2.html로 이동";
                teamDiv.appendChild(link);

                board.appendChild(teamDiv);
            });
        })
        .catch((err) => {
            alert("팀 데이터를 불러오지 못했습니다.");
            console.error(err);
        });
});
