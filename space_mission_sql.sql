-- ===========================================
-- Space Mission Management System
-- Submission SQL File (DDL + DML + Validation)
-- ===========================================

-- 1) DATABASE 생성
DROP DATABASE IF EXISTS space_mission_db;
CREATE DATABASE space_mission_db;
USE space_mission_db;

-- ===========================================
-- 2) DDL (테이블 구조 정의)
-- ===========================================

CREATE TABLE Astronaut (
    astronaut_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    nationality VARCHAR(50),
    astronaut_rank VARCHAR(50),
    experience_years INT DEFAULT 0
);

CREATE TABLE Spacecraft (
    spacecraft_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(100),
    build_year YEAR,
    status ENUM('정상','점검','고장','수리중') DEFAULT '정상'
);

CREATE TABLE Mission (
    mission_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    mission_name VARCHAR(150) NOT NULL,
    goal TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    status ENUM('예정','진행','완료','실패') DEFAULT '예정',
    spacecraft_id INT UNSIGNED NOT NULL,
    FOREIGN KEY (spacecraft_id) REFERENCES Spacecraft(spacecraft_id)
);

CREATE TABLE Equipment (
    equipment_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    manufacturer VARCHAR(100),
    status ENUM('작동','고장','점검') DEFAULT '작동'
);

CREATE TABLE Mission_Astronaut (
    mission_id INT UNSIGNED,
    astronaut_id INT UNSIGNED,
    role VARCHAR(50),
    PRIMARY KEY (mission_id, astronaut_id),
    FOREIGN KEY (mission_id) REFERENCES Mission(mission_id),
    FOREIGN KEY (astronaut_id) REFERENCES Astronaut(astronaut_id)
);

CREATE TABLE Mission_Equipment (
    mission_id INT UNSIGNED,
    equipment_id INT UNSIGNED,
    usage_note TEXT,
    PRIMARY KEY (mission_id, equipment_id),
    FOREIGN KEY (mission_id) REFERENCES Mission(mission_id),
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id)
);

CREATE TABLE Mission_Log (
    log_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    mission_id INT UNSIGNED NOT NULL,
    astronaut_id INT UNSIGNED NULL,
    log_time DATETIME NOT NULL,
    message TEXT NOT NULL,
    FOREIGN KEY (mission_id) REFERENCES Mission(mission_id),
    FOREIGN KEY (astronaut_id) REFERENCES Astronaut(astronaut_id)
);

-- ===========================================
-- 3) DML (샘플 데이터 삽입)
-- ===========================================

INSERT INTO Astronaut (name, birth_date, nationality, astronaut_rank, experience_years)
VALUES 
('John Miller', '1984-03-21', 'USA', 'Commander', 12),
('Sato Rina', '1990-07-11', 'Japan', 'Engineer', 5),
('Kim Minjun', '1988-12-02', 'Korea', 'Pilot', 7);

INSERT INTO Spacecraft (name, manufacturer, build_year, status)
VALUES
('Orion-X', 'NASA', 2018, '정상'),
('StarRider', 'SpaceX', 2020, '점검');

INSERT INTO Mission (mission_name, goal, start_date, end_date, status, spacecraft_id)
VALUES
('Mars Exploration Alpha', 'Explore Mars surface.', '2025-03-01', NULL, '진행', 1),
('Lunar Base Deployment', 'Deploy equipment on the Moon.', '2024-10-10', '2024-12-20', '완료', 2);

INSERT INTO Equipment (equipment_name, category, manufacturer, status)
VALUES
('Drill-2000', 'Mining', 'AstroCo', '작동'),
('Laser Scanner L5', 'Scan', 'GalaxyTech', '작동'),
('Life Support Unit', 'Survival', 'OrbitalLabs', '점검');

INSERT INTO Mission_Astronaut (mission_id, astronaut_id, role)
VALUES
(1, 1, 'Commander'),
(1, 2, 'Engineer'),
(2, 3, 'Pilot');

INSERT INTO Mission_Equipment (mission_id, equipment_id, usage_note)
VALUES
(1, 1, 'Used for soil drilling'),
(1, 2, 'Topography scanning'),
(2, 3, 'Support lunar base environment');

INSERT INTO Mission_Log (mission_id, astronaut_id, log_time, message)
VALUES
(1, 1, NOW(), 'Mission started successfully.'),
(1, 2, NOW(), 'Scanner deployed.'),
(2, 3, NOW(), 'Landing sequence completed.');

-- ===========================================
-- 4) 검증 쿼리 (Validation Queries)
-- ===========================================

-- 4-1) 특정 임무에 참여한 우주비행사 목록
SELECT m.mission_name, a.name, ma.role
FROM Mission m
JOIN Mission_Astronaut ma ON m.mission_id = ma.mission_id
JOIN Astronaut a ON ma.astronaut_id = a.astronaut_id
WHERE m.mission_id = 1;

-- 4-2) 특정 우주선이 수행한 임무 목록
SELECT s.name AS spacecraft, m.mission_name, m.status
FROM Spacecraft s
JOIN Mission m ON s.spacecraft_id = m.spacecraft_id
WHERE s.spacecraft_id = 1;

-- 4-3) 특정 임무에서 사용한 장비 조회
SELECT m.mission_name, e.equipment_name, me.usage_note
FROM Mission m
JOIN Mission_Equipment me ON m.mission_id = me.mission_id
JOIN Equipment e ON me.equipment_id = e.equipment_id
WHERE m.mission_id = 1;

-- 4-4) 임무 로그 조회
SELECT m.mission_name, a.name AS astronaut, l.log_time, l.message
FROM Mission_Log l
LEFT JOIN Astronaut a ON l.astronaut_id = a.astronaut_id
JOIN Mission m ON l.mission_id = m.mission_id
ORDER BY l.log_time;