import tkinter as tk
from tkinter import messagebox
import sqlite3

# Database setup
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

# Database helper functions 
def register_user():
    first = entry_first_name.get()
    last = entry_last_name.get()
    email = entry_email.get()
    username = entry_username.get()
    password = entry_password.get()
    phone = entry_phone.get()

    if not (first and last and email and username and password):
        messagebox.showerror("Error", "Please fill in all required fields")
        return

    try:
        conn = sqlite3.connect("musicApp.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, username, password, phone_no)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (first, last, email, username, password, phone))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "User registered successfully!")
        clear_registration_fields()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists!")
    except Exception as e:
        messagebox.showerror("Error", f"Database error: {e}")

def set_current_user_in_db(user_id):
    conn = sqlite3.connect("musicApp.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM current_user")  # Clear previous login
    cursor.execute("INSERT INTO current_user (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

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
        messagebox.showinfo("Welcome", f"Welcome back, {user[1]} {user[2]}!")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

# UI helper functions 
def clear_registration_fields():
    for entry in [entry_first_name, entry_last_name, entry_email, entry_username, entry_password, entry_phone]:
        entry.delete(0, tk.END)

def switch_to_register():
    login_frame.pack_forget()
    register_frame.pack(pady=20)

def switch_to_login():
    register_frame.pack_forget()
    login_frame.pack(pady=20)


root = tk.Tk()
root.title("Music App")
root.geometry("420x550")
root.config(bg="white")  # all background white

def create_label(frame, text):
    return tk.Label(frame, text=text, fg="black", bg="white", font=("Arial", 11))

def create_entry(frame, show=None):
    return tk.Entry(frame, show=show, width=28, font=("Arial", 11), fg="black", bg="white", bd=1, relief="solid", insertbackground="black")

# Login UI 
login_frame = tk.Frame(root, bg="white")
login_frame.pack(pady=60, padx=30)

tk.Label(login_frame, text="Music App Login", font=("Arial", 20, "bold"), fg="black", bg="white").pack(pady=15)

create_label(login_frame, "Username").pack(anchor="w", padx=20)
login_username = create_entry(login_frame)
login_username.pack(padx=20, pady=5)

create_label(login_frame, "Password").pack(anchor="w", padx=20)
login_password = create_entry(login_frame, show="*")
login_password.pack(padx=20, pady=5)

tk.Button(login_frame, text="Login", command=login_user,
          bg="white", fg="black", width=20, height=2,
          bd=1, relief="solid", font=("Arial", 11, "bold")).pack(pady=20)

tk.Label(login_frame, text="Don’t have an account?", bg="white", fg="black").pack()
tk.Button(login_frame, text="Register", command=switch_to_register,
          bg="white", fg="black", width=15, height=1,
          bd=1, relief="solid", font=("Arial", 10, "bold")).pack(pady=5)

# Registration UI 
register_frame = tk.Frame(root, bg="white")

tk.Label(register_frame, text="Register", font=("Arial", 20, "bold"), fg="black", bg="white").pack(pady=15)

for label_text, var_name in [
    ("First Name", "entry_first_name"),
    ("Last Name", "entry_last_name"),
    ("Email", "entry_email"),
    ("Username", "entry_username"),
    ("Password", "entry_password"),
    ("Phone Number", "entry_phone")
]:
    create_label(register_frame, label_text).pack(anchor="w", padx=20)
    entry = create_entry(register_frame, show="*" if label_text == "Password" else None)
    entry.pack(padx=20, pady=5)
    globals()[var_name] = entry

tk.Button(register_frame, text="Submit", command=register_user,
          bg="white", fg="black", width=20, height=2,
          bd=1, relief="solid", font=("Arial", 11, "bold")).pack(pady=15)

tk.Button(register_frame, text="Back to Login", command=switch_to_login,
          bg="white", fg="black", width=20, height=2,
          bd=1, relief="solid", font=("Arial", 11, "bold")).pack()

root.mainloop()
