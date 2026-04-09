import sqlite3
import os
from pathlib import Path

try:
    from .tag import get_description_and_tag_for_image
except ImportError:
    from tag import get_description_and_tag_for_image

# Path to the database file
DB_PATH = "data/screenshots.db"

# The SQL schema as a string; if using your own module, import it as needed.
sql_create_table = """
CREATE TABLE IF NOT EXISTS screenshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    description TEXT,
    tag TEXT NOT NULL,
    processed_at TEXT
);
"""


def create_table():
    """Create the screenshots table if it does not exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(sql_create_table)
    conn.commit()
    conn.close()

def init_db():
    """Initialize the database if it doesn't exist."""
    if not os.path.exists(DB_PATH):
        create_table()
        print(f"Initialized new database at {DB_PATH}")
    else:
        print(f"Database already exists at {DB_PATH}")

def search(query: str):
    """
    Searches the screenshots table for records matching the query in file_name, tag, or description fields.
    Returns a list of matching rows as dictionaries.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = """
        SELECT * FROM screenshots
        WHERE file_name LIKE ?
           OR tag LIKE ?
           OR description LIKE ?
        ORDER BY timestamp DESC
    """
    result = cursor.execute(sql, (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
    conn.close()
    return [dict(row) for row in result]

def add_screenshot(path: str):
    """
    Adds a screenshot to the database after processing if it is not already processed.
    Extracts description and tag using get_description_and_tag_for_image.
    """
    if is_processed(path):
        print(f"Screenshot '{path}' already processed.")
        return

    td_obj = get_description_and_tag_for_image(path)
    description = td_obj.description
    tag = td_obj.tag

    insert_screenshot(path, description, tag)
    print(f"Added screenshot '{path}' with tag '{tag}'.")

def is_processed(path: str):
    """
    Returns True if the screenshot at the given path is already processed (in DB).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM screenshots WHERE file_path = ?", (path,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def insert_screenshot(path: str, description: str, tag: str):
    """
    Inserts a screenshot record into the DB.
    Expects path, description, and tag.
    """
    file_name = os.path.basename(path)
    timestamp = str(int(Path(path).stat().st_mtime))
    processed_at = None  # could set to current timestamp if desired

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO screenshots (file_path, file_name, timestamp, description, tag, processed_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (path, file_name, timestamp, description, tag, processed_at)
    )
    conn.commit()
    conn.close()

def get_stats():
    """
    Returns comprehensive statistics about the database, including:
      - total screenshot count
      - all unique tags
      - a count for each tag
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Total screenshots
        cursor.execute("SELECT COUNT(*) FROM screenshots")
        total_screenshots = cursor.fetchone()[0]

        # All unique tags
        cursor.execute("SELECT DISTINCT tag FROM screenshots")
        all_tags = [row[0] for row in cursor.fetchall()]

        # Count per tag
        cursor.execute("SELECT tag, COUNT(*) FROM screenshots GROUP BY tag")
        tag_counts = {row[0]: row[1] for row in cursor.fetchall()}

    except sqlite3.Error as e:
        print(f"Database error in get_stats: {e}")
        total_screenshots = None
        all_tags = []
        tag_counts = {}
    finally:
        conn.close()

    return {
        "total_screenshots": total_screenshots,
        "all_tags": all_tags,
        "tag_counts": tag_counts,
    }

def search_by_tag(tag: str):
    """
    Searches the screenshots table for records matching the tag.
    Returns a list of matching rows as dictionaries.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = """
        SELECT * FROM screenshots
        WHERE tag = ?
        ORDER BY timestamp DESC
    """
    result = cursor.execute(sql, (tag,)).fetchall()
    conn.close()
    return [dict(row) for row in result]

def get_all_unique_tags():
    """
    Returns a list of all unique tags in the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT tag FROM screenshots")
    result = cursor.fetchall()
    conn.close()
    return [row[0] for row in result]


if __name__ == "__main__":
    init_db()
    add_screenshot("/Users/ten-jampa/Documents/llm-pipeline-portfolio/screenshot-tagger/test-images/me_with_newton.jpg")
    print(search("newton"))
    print(is_processed("/Users/ten-jampa/Documents/llm-pipeline-portfolio/screenshot-tagger/test-images/me_with_newton.jpg"))
    print(get_stats())
    print(search_by_tag("code-snippets"))
    print(get_all_unique_tags())