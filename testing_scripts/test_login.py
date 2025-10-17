# test_loginapp_db.py
import sqlite3
import sys
import os

# Add parent folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from LoginApp import DB_FILE, get_current_user, update_user_profile

TEST_USER = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "username": "testuser123",
    "password": "password",
    "phone_no": "1234567890",
    "profile_pic": ""
}

def setup_test_user():
    """Ensure test user exists and is set as current_user."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create tables if missing
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            username TEXT UNIQUE,
            password TEXT,
            phone_no TEXT,
            profile_pic TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS current_user (
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    conn.commit()

    # Insert test user if not exists
    cursor.execute("SELECT user_id FROM users WHERE username=?", (TEST_USER["username"],))
    row = cursor.fetchone()
    if row:
        user_id = row[0]
    else:
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, username, password, phone_no, profile_pic)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (TEST_USER["first_name"], TEST_USER["last_name"], TEST_USER["email"],
              TEST_USER["username"], TEST_USER["password"], TEST_USER["phone_no"], TEST_USER["profile_pic"]))
        conn.commit()
        user_id = cursor.lastrowid

    # Set as current user
    cursor.execute("DELETE FROM current_user")
    cursor.execute("INSERT INTO current_user (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    return user_id

def test_get_current_user():
    user_id = setup_test_user()
    user = get_current_user()
    assert user is not None, "Failed to get current user"
    assert user["id"] == user_id, "Returned user ID mismatch"
    print("get_current_user() test passed!")

def test_update_user_profile():
    user = get_current_user()
    new_first_name = "Updated"
    new_last_name = "Name"
    update_user_profile(user["id"], new_first_name, new_last_name, user["email"], user["phone_no"], user["profile_pic"])

    updated_user = get_current_user()
    assert updated_user["first_name"] == new_first_name, "First name not updated"
    assert updated_user["last_name"] == new_last_name, "Last name not updated"
    print("update_user_profile() test passed!")

if __name__ == "__main__":
    test_get_current_user()
    test_update_user_profile()
    print("All database tests passed!")
