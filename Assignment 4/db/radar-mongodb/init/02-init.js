// Select database
db = db.getSiblingDB("radar_db");

// --- USER_GROUP ---
db.user_group.insertMany([
    { _id: 1, group_name: "Admins", description: "System Administrators" },
    { _id: 2, group_name: "Operators", description: "Basic Radar Operators" },
    { _id: 3, group_name: "Analysts", description: "Radar Data Analysts" },
    { _id: 4, group_name: "Guests", description: "Limited Access Users" },
    { _id: 5, group_name: "Maintenance", description: "Hardware/Software Technicians" },
    { _id: 6, group_name: "Custom6_1", description: "Custom Group 6 for DB _1" },
    { _id: 7, group_name: "Custom7_1", description: "Custom Group 7 for DB _1" },
    { _id: 8, group_name: "Custom8_1", description: "Custom Group 8 for DB _1" },
    { _id: 9, group_name: "Custom9_1", description: "Custom Group 9 for DB _1" },
    { _id: 10, group_name: "Custom10_1", description: "Custom Group 10 for DB _1" }
]);

// --- USER_ACCOUNT ---
db.user_account.insertMany([
    { _id: 1, group_id: 1, username: "admin", password_hash: "hash_admin", radar_station: 1 },
    { _id: 2, group_id: 2, username: "operator1", password_hash: "hash_op1", radar_station: 1 },
    { _id: 3, group_id: 2, username: "operator2", password_hash: "hash_op2", radar_station: 1 },
    { _id: 4, group_id: 3, username: "analyst1", password_hash: "hash_an1", radar_station: 1 },
    { _id: 5, group_id: 4, username: "guest1", password_hash: "hash_guest1", radar_station: 1 },
    { _id: 6, group_id: 6, username: "user6_1", password_hash: "hash6_1", radar_station: 1 },
    { _id: 7, group_id: 7, username: "user7_1", password_hash: "hash7_1", radar_station: 1 },
    { _id: 8, group_id: 8, username: "user8_1", password_hash: "hash8_1", radar_station: 1 },
    { _id: 9, group_id: 9, username: "user9_1", password_hash: "hash9_1", radar_station: 1 },
    { _id: 10, group_id: 10, username: "user10_1", password_hash: "hash10_1", radar_station: 1 }
]);

// --- PERMISSION ---
db.permission.insertMany([
    { _id: 1, group_id: 1, can_select: true, can_insert: true, can_update: true, can_delete: true },
    { _id: 2, group_id: 2, can_select: true, can_insert: false, can_update: false, can_delete: false },
    { _id: 3, group_id: 3, can_select: true, can_insert: false, can_update: true, can_delete: false },
    { _id: 4, group_id: 4, can_select: false, can_insert: false, can_update: false, can_delete: false },
    { _id: 5, group_id: 5, can_select: true, can_insert: true, can_update: false, can_delete: false },
    { _id: 6, group_id: 6, can_select: true, can_insert: false, can_update: false, can_delete: true },
    { _id: 7, group_id: 7, can_select: false, can_insert: true, can_update: false, can_delete: true },
    { _id: 8, group_id: 8, can_select: true, can_insert: true, can_update: true, can_delete: false },
    { _id: 9, group_id: 9, can_select: false, can_insert: true, can_update: true, can_delete: false },
    { _id: 10, group_id: 10, can_select: true, can_insert: false, can_update: true, can_delete: true }
]);

// --- RADAR_DETECTION_2 ---
db.radar_detection_2.insertMany([
    { _id: 1, radar_id: 2, timestamp: ISODate("2025-01-02T00:00:01Z"), x: 10, y: 20, z: 30, reflection_rate: 0.85 },
    { _id: 2, radar_id: 2, timestamp: ISODate("2025-01-02T00:00:02Z"), x: 11, y: 21, z: 31, reflection_rate: 0.80 },
    { _id: 3, radar_id: 2, timestamp: ISODate("2025-01-02T00:00:03Z"), x: 12, y: 22, z: 32, reflection_rate: 0.90 },
    { _id: 4, radar_id: 2, timestamp: ISODate("2025-01-02T00:00:04Z"), x: 13, y: 23, z: 33, reflection_rate: 0.95 },
    { _id: 5, radar_id: 2, timestamp: ISODate("2025-01-02T00:00:05Z"), x: 14, y: 24, z: 34, reflection_rate: 0.75 },
    { _id: 6, radar_id: 2, timestamp: ISODate("2025-01-02T00:00:06Z"), x: 20, y: 30, z: 40, reflection_rate: 0.61 },
    { _id: 7, radar_id: 2, timestamp: ISODate("2025-01-02T00:00:07Z"), x: 21, y: 31, z: 41, reflection_rate: 0.62 },
    { _id: 8, radar_id: 2, timestamp: ISODate("2025-01-02T00:00:08Z"), x: 22, y: 32, z: 42, reflection_rate: 0.63 },
    { _id: 9, radar_id: 2, timestamp: ISODate("2025-01-02T00:00:09Z"), x: 23, y: 33, z: 43, reflection_rate: 0.64 },
    { _id: 10, radar_id: 2, timestamp: ISODate("2025-01-02T00:00:10Z"), x: 24, y: 34, z: 44, reflection_rate: 0.65 }
]);

// --- AUDIT_LOG_2 ---
db.audit_log_2.insertMany([
    { _id: 1, timestamp: ISODate("2025-01-02T10:00:00Z"), user_id: 1, operation: "LOGIN", radar_station: 2, table_name: "USER_ACCOUNT", description: "Admin logged in" },
    { _id: 2, timestamp: ISODate("2025-01-02T10:01:00Z"), user_id: 2, operation: "SELECT", radar_station: 2, table_name: "RADAR_DETECTION", description: "Operator queried radar data" },
    { _id: 3, timestamp: ISODate("2025-01-02T10:02:00Z"), user_id: 3, operation: "SELECT", radar_station: 2, table_name: "RADAR_DETECTION", description: "Operator2 queried radar data" },
    { _id: 4, timestamp: ISODate("2025-01-02T10:03:00Z"), user_id: 4, operation: "UPDATE", radar_station: 2, table_name: "USER_ACCOUNT", description: "Analyst updated profile" },
    { _id: 5, timestamp: ISODate("2025-01-02T10:04:00Z"), user_id: 5, operation: "LOGIN", radar_station: 2, table_name: "USER_ACCOUNT", description: "Guest login" },
    { _id: 6, timestamp: ISODate("2025-01-02T10:05:00Z"), user_id: 6, operation: "LOGIN", radar_station: 2, table_name: "USER_ACCOUNT", description: "Custom user6_1 login" },
    { _id: 7, timestamp: ISODate("2025-01-02T10:06:00Z"), user_id: 7, operation: "INSERT", radar_station: 2, table_name: "AUDIT_LOG", description: "Custom user7_1 insert" },
    { _id: 8, timestamp: ISODate("2025-01-02T10:07:00Z"), user_id: 8, operation: "DELETE", radar_station: 2, table_name: "RADAR_DETECTION", description: "Custom user8_1 delete attempt" },
    { _id: 9, timestamp: ISODate("2025-01-02T10:08:00Z"), user_id: 9, operation: "UPDATE", radar_station: 2, table_name: "USER_GROUP", description: "Custom user9_1 updated group" },
    { _id: 10, timestamp: ISODate("2025-01-02T10:09:00Z"), user_id: 10, operation: "SELECT", radar_station: 2, table_name: "PERMISSION", description: "Custom user10_1 select" }
]);
