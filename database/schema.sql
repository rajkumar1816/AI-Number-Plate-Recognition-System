CREATE TABLE IF NOT EXISTS vehicle_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_name TEXT,
    plate_number TEXT,
    confidence REAL,
    date TEXT,
    time TEXT,
    image_path TEXT,
    cropped_path TEXT
);

CREATE TABLE IF NOT EXISTS blacklist_vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number TEXT UNIQUE,
    added_at TEXT
);
