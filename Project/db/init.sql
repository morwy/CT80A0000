-- Start up operations.

DROP DATABASE IF EXISTS radar_db;
CREATE DATABASE radar_db;
USE radar_db;

-- Default project schema.
-- Each database should contain a minimum of group members x 2 (6, 8 or 10) of tables/collections.
-- Each table should contain a reasonable amount of attributes (not just ID and one attribute), 
--      roughly +4 attributes (sometimes you can have less if they are joining tables).

CREATE TABLE RADAR_DETECTION(
    detection_id INT PRIMARY KEY AUTO_INCREMENT,
    radar_id INT,
    timestamp DATETIME,
    x FLOAT,
    y FLOAT,
    z FLOAT,
    reflection_rate FLOAT
);

CREATE TABLE USER_GROUP(
    group_id INT PRIMARY KEY AUTO_INCREMENT,
    group_name VARCHAR(255),
    description VARCHAR(255)
);

CREATE TABLE USER_ACCOUNT(
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    group_id INT,
    username VARCHAR(255),
    password_hash VARCHAR(255),
    radar_station INT,
    FOREIGN KEY (group_id) REFERENCES USER_GROUP(group_id)
);

CREATE TABLE PERMISSION(
    permission_id INT PRIMARY KEY AUTO_INCREMENT,
    group_id INT,
    can_select BOOLEAN,
    can_insert BOOLEAN,
    can_update BOOLEAN,
    can_delete BOOLEAN,
    FOREIGN KEY (group_id) REFERENCES USER_GROUP(group_id)
);

CREATE TABLE AUDIT_LOG(
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    timestamp DATETIME,
    user_id INT,
    operation VARCHAR(255),
    radar_station INT,
    table_name VARCHAR(255),
    description VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT(user_id)
);

-- Sample data insertion.
-- Each table should contain a minimum of 30 data entries.
-- Some redundant data and bloating is present...

INSERT INTO USER_GROUP (group_id, group_name, description) VALUES
(1,'Unauthorized','No Access Users'),
(2,'Radars','Radars themselves'),

(3,'High-Rank Officers @ RS1','Full Access Users located at Radar Station 1'),
(4,'Officers @ RS1','Limited Access Users located at Radar Station 1'),
(5,'Soldiers @ RS1','Basic Access Users located at Radar Station 1'),
(6,'Technicians @ RS1','Maintenance Users located at Radar Station 1'),
(7,'Administrators @ RS1','Admin Users located at Radar Station 1'),

(8,'High-Rank Officers @ RS2','Full Access Users located at Radar Station 2'),
(9,'Officers @ RS2','Limited Access Users located at Radar Station 2'),
(10,'Soldiers @ RS2','Basic Access Users located at Radar Station 2'),
(11,'Technicians @ RS2','Maintenance Users located at Radar Station 2'),
(12,'Administrators @ RS2','Admin Users located at Radar Station 2'),

(13,'High-Rank Officers @ RS3','Full Access Users located at Radar Station 3'),
(14,'Officers @ RS3','Limited Access Users located at Radar Station 3'),
(15,'Soldiers @ RS3','Basic Access Users located at Radar Station 3'),
(16,'Technicians @ RS3','Maintenance Users located at Radar Station 3'),
(17,'Administrators @ RS3','Admin Users located at Radar Station 3'),

(18,'High-Rank Officers @ RS4','Full Access Users located at Radar Station 4'),
(19,'Officers @ RS4','Limited Access Users located at Radar Station 4'),
(20,'Soldiers @ RS4','Basic Access Users located at Radar Station 4'),
(21,'Technicians @ RS4','Maintenance Users located at Radar Station 4'),
(22,'Administrators @ RS4','Admin Users located at Radar Station 4'),

(23,'High-Rank Officers @ RS5','Full Access Users located at Radar Station 5'),
(24,'Officers @ RS5','Limited Access Users located at Radar Station 5'),
(25,'Soldiers @ RS5','Basic Access Users located at Radar Station 5'),
(26,'Technicians @ RS5','Maintenance Users located at Radar Station 5'),
(27,'Administrators @ RS5','Admin Users located at Radar Station 5'),

(28,'High-Rank Officers @ RS6','Full Access Users located at Radar Station 6'),
(29,'Officers @ RS6','Limited Access Users located at Radar Station 6'),
(30,'Soldiers @ RS6','Basic Access Users located at Radar Station 6'),
(31,'Technicians @ RS6','Maintenance Users located at Radar Station 6'),
(32,'Administrators @ RS6','Admin Users located at Radar Station 6');

INSERT INTO USER_ACCOUNT (user_id, group_id, username, password_hash, radar_station) VALUES
(1,1,'unauthorized_user','hash_unauthorized',0),

(2,2,'radar_1','hash_radar_1',1),
(3,2,'radar_2','hash_radar_2',2),
(4,2,'radar_3','hash_radar_3',3),
(5,2,'radar_4','hash_radar_4',4),
(6,2,'radar_5','hash_radar_5',5),
(7,2,'radar_6','hash_radar_6',6),

(8,3,'high_rank_officer_rs1','hash_hro_rs1',1),
(9,4,'officer_rs1','hash_officer_rs1',1),
(10,5,'soldier_rs1','hash_soldier_rs1',1),
(11,6,'technician_rs1','hash_technician_rs1',1),
(12,7,'administrator_rs1','hash_administrator_rs1',1),

(13,8,'high_rank_officer_rs2','hash_hro_rs2',2),
(14,9,'officer_rs2','hash_officer_rs2',2),
(15,10,'soldier_rs2','hash_soldier_rs2',2),
(16,11,'technician_rs2','hash_technician_rs2',2),
(17,12,'administrator_rs2','hash_administrator_rs2',2),

(18,13,'high_rank_officer_rs3','hash_hro_rs3',3),
(19,14,'officer_rs3','hash_officer_rs3',3),
(20,15,'soldier_rs3','hash_soldier_rs3',3),
(21,16,'technician_rs3','hash_technician_rs3',3),
(22,17,'administrator_rs3','hash_administrator_rs3',3),

(23,18,'high_rank_officer_rs4','hash_hro_rs4',4),
(24,19,'officer_rs4','hash_officer_rs4',4),
(25,20,'soldier_rs4','hash_soldier_rs4',4),
(26,21,'technician_rs4','hash_technician_rs4',4),
(27,22,'administrator_rs4','hash_administrator_rs4',4),

(28,23,'high_rank_officer_rs5','hash_hro_rs5',5),
(29,24,'officer_rs5','hash_officer_rs5',5),
(30,25,'soldier_rs5','hash_soldier_rs5',5),
(31,26,'technician_rs5','hash_technician_rs5',5),
(32,27,'administrator_rs5','hash_administrator_rs5',5),

(33,28,'high_rank_officer_rs6','hash_hro_rs6',6),
(34,29,'officer_rs6','hash_officer_rs6',6),
(35,30,'soldier_rs6','hash_soldier_rs6',6),
(36,31,'technician_rs6','hash_technician_rs6',6),
(37,32,'administrator_rs6','hash_administrator_rs6',6);

INSERT INTO PERMISSION (permission_id, group_id, can_select, can_insert, can_update, can_delete) VALUES
(1,1,FALSE,FALSE,FALSE,FALSE),
(2,2,FALSE,TRUE,FALSE,FALSE),

(3,3,TRUE,TRUE,TRUE,TRUE),
(4,4,TRUE,TRUE,FALSE,FALSE),
(5,5,TRUE,FALSE,FALSE,FALSE),
(6,6,TRUE,TRUE,TRUE,FALSE),
(7,7,TRUE,TRUE,TRUE,TRUE),

(8,8,TRUE,TRUE,TRUE,TRUE),
(9,9,TRUE,TRUE,FALSE,FALSE),
(10,10,TRUE,FALSE,FALSE,FALSE),
(11,11,TRUE,TRUE,TRUE,FALSE),
(12,12,TRUE,TRUE,TRUE,TRUE),

(13,13,TRUE,TRUE,TRUE,TRUE),
(14,14,TRUE,TRUE,FALSE,FALSE),
(15,15,TRUE,FALSE,FALSE,FALSE),
(16,16,TRUE,TRUE,TRUE,FALSE),
(17,17,TRUE,TRUE,TRUE,TRUE),

(18,18,TRUE,TRUE,TRUE,TRUE),
(19,19,TRUE,TRUE,FALSE,FALSE),
(20,20,TRUE,FALSE,FALSE,FALSE),
(21,21,TRUE,TRUE,TRUE,FALSE),
(22,22,TRUE,TRUE,TRUE,TRUE),

(23,23,TRUE,TRUE,TRUE,TRUE),
(24,24,TRUE,TRUE,FALSE,FALSE),
(25,25,TRUE,FALSE,FALSE,FALSE),
(26,26,TRUE,TRUE,TRUE,FALSE),
(27,27,TRUE,TRUE,TRUE,TRUE),

(28,28,TRUE,TRUE,TRUE,TRUE),
(29,29,TRUE,TRUE,FALSE,FALSE),
(30,30,TRUE,FALSE,FALSE,FALSE),
(31,31,TRUE,TRUE,TRUE,FALSE),
(32,32,TRUE,TRUE,TRUE,TRUE);

-- The data includes multiple aircraft trajectories, weather phenomena, and random noise.
INSERT INTO RADAR_DETECTION (detection_id, radar_id, timestamp, x, y, z, reflection_rate) VALUES
-- Plane 1
(1,  2, '2025-01-01 10:00:00',   50.0, -120.5,  9.8, 12.4),
(2,  2, '2025-01-01 10:01:00',  120.0, -115.0, 10.1, 12.6),
(3,  2, '2025-01-01 10:02:00',  190.0, -110.2, 10.5, 12.7),
(4,  1, '2025-01-01 10:03:00',  260.0, -105.0, 10.8, 12.9),
(5,  1, '2025-01-01 10:04:00',  330.0, -100.1, 11.2, 13.0),
(6,  1, '2025-01-01 10:05:00',  400.0,  -95.4, 11.5, 13.1),
(7,  1, '2025-01-01 10:06:00',  470.0,  -90.0, 11.9, 13.3),
(8,  1, '2025-01-01 10:07:00',  540.0,  -85.3, 12.2, 13.4),
(9,  1, '2025-01-01 10:08:00',  610.0,  -80.0, 12.6, 13.5),
(10, 1, '2025-01-01 10:09:00',  680.0,  -75.5, 12.9, 13.7),

-- Plane 2
(11, 2, '2025-01-01 10:00:00',  -30.0, 80.0, 10.0, 11.8),
(12, 2, '2025-01-01 10:01:00', -100.0, 82.5, 10.3, 11.9),
(13, 2, '2025-01-01 10:02:00', -170.0, 85.0, 10.7, 12.0),
(14, 3, '2025-01-01 10:03:00', -240.0, 87.4, 11.0, 12.2),
(15, 3, '2025-01-01 10:04:00', -310.0, 90.0, 11.4, 12.3),
(16, 3, '2025-01-01 10:05:00', -380.0, 92.6, 11.7, 12.4),
(17, 3, '2025-01-01 10:06:00', -450.0, 95.0, 12.1, 12.6),
(18, 3, '2025-01-01 10:07:00', -520.0, 97.5, 12.4, 12.7),
(19, 3, '2025-01-01 10:08:00', -590.0,100.0, 12.8, 12.8),
(20, 3, '2025-01-01 10:09:00', -660.0,102.5, 13.1, 13.0),

-- Plane 3
(21,2,'2025-01-01 10:00:00', -150.0,  20.0, 12.0, 11.5),
(22,2,'2025-01-01 10:01:00', -120.0,  22.0, 12.0, 11.6),
(23,2,'2025-01-01 10:02:00',  -90.0,  25.0, 12.0, 11.7),
(24,2,'2025-01-01 10:03:00',  -60.0,  27.0, 12.0, 11.8),
(25,2,'2025-01-01 10:04:00',  -30.0,  30.0, 12.0, 11.9),
(26,2,'2025-01-01 10:05:00',    0.0,  32.0, 12.0, 12.0),
(27,2,'2025-01-01 10:06:00',   30.0,  35.0, 12.0, 12.1),
(28,2,'2025-01-01 10:07:00',   60.0,  37.0, 12.0, 12.2),
(29,2,'2025-01-01 10:08:00',   90.0,  40.0, 12.0, 12.3),
(30,2,'2025-01-01 10:09:00',  120.0,  42.0, 12.0, 12.4),

-- Cloud
(31,1,'2025-01-01 10:00:00',  800.0, 40.0, 6.0, 45.0),
(32,1,'2025-01-01 10:01:00',  805.0, 42.0, 6.1, 46.0),
(33,1,'2025-01-01 10:02:00',  798.0, 41.0, 6.0, 44.8),
(34,1,'2025-01-01 10:03:00',  802.0, 43.5, 6.2, 45.5),
(35,1,'2025-01-01 10:04:00',  810.0, 44.0, 6.1, 46.2),
(36,1,'2025-01-01 10:05:00',  807.0, 42.5, 6.3, 45.7),
(37,1,'2025-01-01 10:06:00',  803.0, 41.0, 6.2, 45.3),
(38,1,'2025-01-01 10:07:00',  809.0, 43.0, 6.4, 46.1),
(39,1,'2025-01-01 10:08:00',  811.0, 44.5, 6.3, 46.5),
(40,1,'2025-01-01 10:09:00',  808.0, 42.0, 6.5, 45.9),

-- Digital noise
(41,2,'2025-01-01 10:00:00', -33.2,   44.0,  2.1, 0.6),
(42,3,'2025-01-01 10:01:00',  77.8, -512.0,  1.5, 0.4),
(43,1,'2025-01-01 10:02:00', -10.0,  600.0,  0.8, 0.5),
(44,2,'2025-01-01 10:03:00', 120.0,  -80.0,  1.2, 0.3),
(45,3,'2025-01-01 10:04:00', -95.0, -720.0,  2.0, 0.7),
(46,1,'2025-01-01 10:05:00',  45.0,  350.0,  1.0, 0.4),
(47,2,'2025-01-01 10:06:00', -60.0,   90.0,  0.5, 0.2),
(48,3,'2025-01-01 10:07:00', 300.0, -400.0,  1.8, 0.6),
(49,1,'2025-01-01 10:08:00', -25.0,  480.0,  2.3, 0.5),
(50,2,'2025-01-01 10:09:00', 150.0, -150.0,  1.1, 0.3);

INSERT INTO AUDIT_LOG (log_id, timestamp, user_id, operation, radar_station, table_name, description) VALUES
(1,'2025-01-01 10:00:00',1,'LOGIN_ATTEMPT',1,'USER_ACCOUNT','Unauthorized user attempted to log in.'),
(2,'2025-01-01 10:05:00',8,'DELETE',1,'RADAR_DETECTION','High-Rank Officer at RS1 deleted a radar detection.'),
(3,'2025-01-01 10:10:00',9,'SELECT',1,'RADAR_DETECTION','Officer at RS1 viewed radar detections.'),
(4,'2025-01-01 10:15:00',10,'SELECT',1,'RADAR_DETECTION','Soldier at RS1 viewed radar detections.'),
(5,'2025-01-01 10:20:00',11,'UPDATE',1,'RADAR_DETECTION','Technician at RS1 updated a radar detection.'),
(6,'2025-01-01 10:25:00',12,'DELETE',1,'RADAR_DETECTION','Administrator at RS1 deleted a radar detection.'),
(7,'2025-01-01 10:30:00',13,'DELETE',2,'RADAR_DETECTION','High-Rank Officer at RS2 deleted a radar detection.'),
(8,'2025-01-01 10:35:00',14,'SELECT',2,'RADAR_DETECTION','Officer at RS2 viewed radar detections.'),
(9,'2025-01-01 10:40:00',15,'SELECT',2,'RADAR_DETECTION','Soldier at RS2 viewed radar detections.'),
(10,'2025-01-01 10:45:00',16,'UPDATE',2,'RADAR_DETECTION','Technician at RS2 updated a radar detection.'),
(11,'2025-01-01 10:50:00',17,'LOGIN_SUCCESS',2,'USER_ACCOUNT','User logged in.'),
(12,'2025-01-01 10:55:00',2,'INSERT',1,'RADAR_DETECTION','Radar 1 inserted a new radar detection.'),
(13,'2025-01-01 11:00:00',3,'INSERT',2,'RADAR_DETECTION','Radar 2 inserted a new radar detection.'),
(14,'2025-01-01 11:05:00',4,'INSERT',3,'RADAR_DETECTION','Radar 3 inserted a new radar detection.'),
(15,'2025-01-01 11:10:00',5,'INSERT',4,'RADAR_DETECTION','Radar 4 inserted a new radar detection.'),
(16,'2025-01-01 11:15:00',6,'INSERT',5,'RADAR_DETECTION','Radar 5 inserted a new radar detection.'),
(17,'2025-01-01 11:20:00',7,'INSERT',6,'RADAR_DETECTION','Radar 6 inserted a new radar detection.'),
(18, '2025-01-01 11:30:00',1,'LOGIN_ATTEMPT',3,'USER_ACCOUNT','Unauthorized user attempted to log in.'),
(19, '2025-01-01 11:25:00',1,'LOGIN_FAILURE',3,'USER_ACCOUNT','User failed to log in.'),
(20, '2025-01-01 11:35:00',1,'LOGIN_ATTEMPT',4,'USER_ACCOUNT','Unauthorized user attempted to log in.'),
(21, '2025-01-01 11:26:00',1,'LOGIN_FAILURE',3,'USER_ACCOUNT','User failed to log in.'),
(22, '2025-01-01 11:40:00',1,'LOGIN_ATTEMPT',5,'USER_ACCOUNT','Unauthorized user attempted to log in.'),
(23, '2025-01-01 11:46:00',1,'LOGIN_FAILURE',3,'USER_ACCOUNT','User failed to log in.'),
(24, '2025-01-01 11:45:00',1,'LOGIN_ATTEMPT',6,'USER_ACCOUNT','Unauthorized user attempted to log in.'),
(25, '2025-01-01 11:46:00',1,'LOGIN_FAILURE',3,'USER_ACCOUNT','User failed to log in.'),
(26, '2025-01-01 11:46:00',8,'LOGOUT_SUCCESS',1,'USER_ACCOUNT','User logged out.'),
(27, '2025-01-01 11:50:00',9,'LOGOUT_SUCCESS',2,'USER_ACCOUNT','User logged out.'),
(28, '2025-01-01 11:55:00',10,'LOGOUT_SUCCESS',3,'USER_ACCOUNT','User logged out.'),
(29, '2025-01-01 12:00:00',11,'LOGOUT_SUCCESS',4,'USER_ACCOUNT','User logged out.'),
(30, '2025-01-01 12:05:00',12,'LOGOUT_SUCCESS',5,'USER_ACCOUNT','User logged out.'),
(31, '2025-01-01 12:10:00',8,'LOGIN_SUCCESS',6,'USER_ACCOUNT','User logged in.');
