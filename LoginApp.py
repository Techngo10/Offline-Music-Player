# LoginApp.py
import tkinter as tk
from tkinter import messagebox
import sqlite3

DB_FILE = "musicApp.db"

def show_login():
    result = {"user_id": None}

    def initialize_database():
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
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

    def set_current_user_in_db(user_id):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM current_user")  # clear previous login
        cursor.execute("INSERT INTO current_user (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        result["user_id"] = user_id
        login_root.destroy()

    # ---------------- LOGIN ----------------
    def login_user():
        username = login_username.get()
        password = login_password.get()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            set_current_user_in_db(user[0])
        else:
            messagebox.showerror("Error", "Invalid username or password")

    # ---------------- REGISTER ----------------
    def open_register():
        reg_window = tk.Toplevel(login_root)
        reg_window.title("Register Account")
        reg_window.geometry("400x400")
        reg_window.config(bg="white")

        tk.Label(reg_window, text="Register New Account", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        fields = ["First Name", "Last Name", "Username", "Password", "Email", "Phone No"]
        entries = {}

        for field in fields:
            tk.Label(reg_window, text=field, bg="white").pack()
            entry = tk.Entry(reg_window, show="*" if field=="Password" else None)
            entry.pack(pady=5)
            entries[field] = entry

        def register_user():
            first = entries["First Name"].get().strip()
            last = entries["Last Name"].get().strip()
            username = entries["Username"].get().strip()
            password = entries["Password"].get().strip()
            email = entries["Email"].get().strip()
            phone = entries["Phone No"].get().strip()

            if not (first and last and username and password):
                messagebox.showwarning("Missing info", "Please fill in all required fields")
                return

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO users (first_name, last_name, username, password, email, phone_no)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (first, last, username, password, email, phone))
                conn.commit()
                user_id = cursor.lastrowid
                messagebox.showinfo("Success", "Account created successfully!")
                reg_window.destroy()
                set_current_user_in_db(user_id)
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists")
            finally:
                conn.close()

        tk.Button(reg_window, text="Register", command=register_user).pack(pady=20)

    # ---------------- LOGIN WINDOW ----------------
    login_root = tk.Tk()
    login_root.title("Music App Login")
    login_root.attributes('-fullscreen', True)
    login_root.config(bg="white")

    tk.Label(login_root, text="Music App Login", font=("Arial", 20, "bold"), bg="white").pack(pady=20)
    tk.Label(login_root, text="Username", bg="white").pack()
    login_username = tk.Entry(login_root)
    login_username.pack(pady=5)
    tk.Label(login_root, text="Password", bg="white").pack()
    login_password = tk.Entry(login_root, show="*")
    login_password.pack(pady=5)
    tk.Button(login_root, text="Login", command=login_user).pack(pady=10)
    tk.Button(login_root, text="Register New Account", command=open_register).pack(pady=5)

    login_root.mainloop()
    return result["user_id"]
