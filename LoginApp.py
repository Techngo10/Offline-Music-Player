# LoginApp.py
import tkinter as tk
from tkinter import messagebox
import sqlite3

def show_login():
    result = {"user_id": None}

    def initialize_database():
        conn = sqlite3.connect("musicApp.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                phone_no TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS current_user (
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        conn.commit()
        conn.close()

    initialize_database()

    # Login functions
    def set_current_user_in_db(user_id):
        conn = sqlite3.connect("musicApp.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM current_user")  # Clear previous login
        cursor.execute("INSERT INTO current_user (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        result["user_id"] = user_id
        login_root.destroy()  # close login window after success

    def login_user():
        username = login_username.get()
        password = login_password.get()
        conn = sqlite3.connect("musicApp.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            set_current_user_in_db(user[0])
        else:
            messagebox.showerror("Invalid username or password")

    login_root = tk.Tk()
    login_root.title("Music App Login")
    login_root.attributes('-fullscreen', True)  
    login_root.config(bg="white")

    # UI elements simplified
    tk.Label(login_root, text="Music App Login", font=("Arial", 20, "bold")).pack(pady=20)
    tk.Label(login_root, text="Username").pack()
    login_username = tk.Entry(login_root)
    login_username.pack(pady=5)
    tk.Label(login_root, text="Password").pack()
    login_password = tk.Entry(login_root, show="*")
    login_password.pack(pady=5)
    tk.Button(login_root, text="Login", command=login_user).pack(pady=20)

    login_root.mainloop()
    return result["user_id"]
