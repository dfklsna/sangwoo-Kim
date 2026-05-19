import React, { useState, useEffect } from 'react';
import axios from 'axios';

function TeamList({ roomCode, password }) {
  const [teams, setTeams] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get('/api/team-list/', {
      params: {
        room_code: roomCode,
        password: password
      }
    })
    .then(response => {
      setTeams(response.data.teams);
    })
    .catch(error => {
      console.error(error);
      setError("팀 목록을 불러오는 중 오류가 발생했습니다.");
    });
  }, [roomCode, password]);

  return (
    <div>
      <h2>팀 목록</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {Object.keys(teams).map(teamNum => (
        <div key={teamNum} style={{ marginBottom: '20px' }}>
          <h3>{teamNum}조</h3>
          <ul>
            {teams[teamNum].map(member => (
              <li key={member.id}>
                {member.name} ({member.position}) {member.is_leader && "⭐"}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export default TeamList;
