-- Start up operations.

DROP DATABASE IF EXISTS radar_db;
CREATE DATABASE radar_db;
USE radar_db;

-- Default project schema.

CREATE TABLE USER_GROUP(
    _id INT PRIMARY KEY,
    group_name VARCHAR(50),
    description VARCHAR(255)
);

CREATE TABLE USER_ACCOUNT(
    _id INT PRIMARY KEY,
    group_id INT,
    username VARCHAR(50),
    password_hash VARCHAR(255),
    radar_station INT,
    FOREIGN KEY (group_id) REFERENCES USER_GROUP(_id)
);

CREATE TABLE PERMISSION(
    _id INT PRIMARY KEY,
    group_id INT,
    can_select BOOLEAN,
    can_insert BOOLEAN,
    can_update BOOLEAN,
    can_delete BOOLEAN,
    FOREIGN KEY (group_id) REFERENCES USER_GROUP(_id)
);

CREATE TABLE RADAR_DETECTION_1(
    _id INT PRIMARY KEY,
    radar_id INT,
    timestamp DATETIME,
    x FLOAT,
    y FLOAT,
    z FLOAT,
    reflection_rate FLOAT
);

CREATE TABLE AUDIT_LOG_1(
    _id BIGINT PRIMARY KEY,
    timestamp DATETIME,
    user_id INT,
    operation VARCHAR(20),
    radar_station INT,
    table_name VARCHAR(50),
    description VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT(_id)
);

-- Sample data insertion.
-- USER_GROUP, USER_ACCOUNT, PERMISSION tables are the same and RADAR_DETECTION_1, AUDIT_LOG_1 tables is different.

INSERT INTO USER_GROUP (_id, group_name, description) VALUES
(1,'Admins','System Administrators'),
(2,'Operators','Basic Radar Operators'),
(3,'Analysts','Radar Data Analysts'),
(4,'Guests','Limited Access Users'),
(5,'Maintenance','Hardware/Software Technicians'),
(6,'Custom6_1','Custom Group 6 for DB _1'),
(7,'Custom7_1','Custom Group 7 for DB _1'),
(8,'Custom8_1','Custom Group 8 for DB _1'),
(9,'Custom9_1','Custom Group 9 for DB _1'),
(10,'Custom10_1','Custom Group 10 for DB _1');

INSERT INTO USER_ACCOUNT (_id, group_id, username, password_hash, radar_station) VALUES
(1,1,'admin','hash_admin',1),
(2,2,'operator1','hash_op1',1),
(3,2,'operator2','hash_op2',1),
(4,3,'analyst1','hash_an1',1),
(5,4,'guest1','hash_guest1',1),
(6,6,'user6_1','hash6_1',1),
(7,7,'user7_1','hash7_1',1),
(8,8,'user8_1','hash8_1',1),
(9,9,'user9_1','hash9_1',1),
(10,10,'user10_1','hash10_1',1);

INSERT INTO PERMISSION (_id, group_id, can_select, can_insert, can_update, can_delete) VALUES
(1,1,TRUE,TRUE,TRUE,TRUE),
(2,2,TRUE,FALSE,FALSE,FALSE),
(3,3,TRUE,FALSE,TRUE,FALSE),
(4,4,FALSE,FALSE,FALSE,FALSE),
(5,5,TRUE,TRUE,FALSE,FALSE),
(6,6,TRUE,FALSE,FALSE,TRUE),
(7,7,FALSE,TRUE,FALSE,TRUE),
(8,8,TRUE,TRUE,TRUE,FALSE),
(9,9,FALSE,TRUE,TRUE,FALSE),
(10,10,TRUE,FALSE,TRUE,TRUE);

INSERT INTO RADAR_DETECTION_1 (_id, radar_id, timestamp, x, y, z, reflection_rate) VALUES
(1,1,'2025-01-01 00:00:01',10,20,30,0.85),
(2,1,'2025-01-01 00:00:02',11,21,31,0.80),
(3,1,'2025-01-01 00:00:03',12,22,32,0.90),
(4,1,'2025-01-01 00:00:04',13,23,33,0.95),
(5,1,'2025-01-01 00:00:05',14,24,34,0.75),
(6,1,'2025-01-01 00:00:06',20,30,40,0.61),
(7,1,'2025-01-01 00:00:07',21,31,41,0.62),
(8,1,'2025-01-01 00:00:08',22,32,42,0.63),
(9,1,'2025-01-01 00:00:09',23,33,43,0.64),
(10,1,'2025-01-01 00:00:10',24,34,44,0.65);

INSERT INTO AUDIT_LOG_1 (_id, timestamp, user_id, operation, radar_station, table_name, description) VALUES
(1,'2025-01-01 10:00:00',1,'LOGIN',1,'USER_ACCOUNT','Admin logged in'),
(2,'2025-01-01 10:01:00',2,'SELECT',1,'RADAR_DETECTION','Operator queried radar data'),
(3,'2025-01-01 10:02:00',3,'SELECT',1,'RADAR_DETECTION','Operator2 queried radar data'),
(4,'2025-01-01 10:03:00',4,'UPDATE',1,'USER_ACCOUNT','Analyst updated profile'),
(5,'2025-01-01 10:04:00',5,'LOGIN',1,'USER_ACCOUNT','Guest login'),
(6,'2025-01-01 10:05:00',6,'LOGIN',1,'USER_ACCOUNT','Custom user6_1 login'),
(7,'2025-01-01 10:06:00',7,'INSERT',1,'AUDIT_LOG','Custom user7_1 insert'),
(8,'2025-01-01 10:07:00',8,'DELETE',1,'RADAR_DETECTION','Custom user8_1 delete attempt'),
(9,'2025-01-01 10:08:00',9,'UPDATE',1,'USER_GROUP','Custom user9_1 updated group'),
(10,'2025-01-01 10:09:00',10,'SELECT',1,'PERMISSION','Custom user10_1 select');
