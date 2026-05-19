document.addEventListener("DOMContentLoaded", () => {
    const roomCode = new URLSearchParams(location.search).get("code");
    const password = new URLSearchParams(location.search).get("pw");

    if (!roomCode || !password) {
        alert("방 정보가 유효하지 않습니다.");
        return;
    }

    fetch("/api/survey_status/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room_code: roomCode, password: password })
    })
    .then(res => {
        if (!res.ok) throw new Error("응답 현황을 불러올 수 없습니다.");
        return res.json();
    })
    .then(data => {
        // 진행률 표시
        document.getElementById("progress-count").textContent = data.progress;
        document.getElementById("progress-percent").textContent =
            `${data.responded && data.total ? Math.round((data.responded / data.total) * 100) : 0}%`;

        // 미제출자 명단
        renderUnsubmitted(data.unsubmitted);
    })
    .catch(err => {
        alert("상태를 불러오는 데 실패했습니다.");
        console.error(err);
    });
});

function renderUnsubmitted(unsubmitted) {
    const list = document.getElementById("member-list");
    if (unsubmitted.length === 0) {
        list.innerHTML = `<p>미제출자 없음</p>`;
    } else {
        list.innerHTML = unsubmitted.map(name => `<p><strong>${name}</strong></p>`).join("");
    }
}
