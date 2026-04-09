CREATE TABLE IF NOT EXISTS screenshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    description TEXT,
    tag TEXT NOT NULL,
    processed_at TEXT
);