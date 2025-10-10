import tkinter as tk
from tkinter import messagebox
import sqlite3
from Databases import setup_database

setup_database()

# -------------------- Database helper functions --------------------
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

def login_user():
    username = login_username.get()
    password = login_password.get()

    conn = sqlite3.connect("musicApp.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        messagebox.showinfo("Login Successful", f"Welcome {user[1]} {user[2]}!")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

# -------------------- UI helper functions --------------------
def clear_registration_fields():
    entry_first_name.delete(0, tk.END)
    entry_last_name.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    entry_phone.delete(0, tk.END)

def switch_to_register():
    login_frame.pack_forget()
    register_frame.pack(pady=20)

def switch_to_login():
    register_frame.pack_forget()
    login_frame.pack(pady=20)

# -------------------- Tkinter UI --------------------
root = tk.Tk()
root.title("Music App Login")
root.geometry("420x550")
root.config(bg="#f3f6fa")  # Light background

# --- Styling variables ---
BG_COLOR = "#f3f6fa"
CARD_COLOR = "#ffffff"
BUTTON_COLOR = "#4A90E2"
TEXT_COLOR = "#333333"

# --- Common style helper ---
def create_label(frame, text):
    return tk.Label(frame, text=text, fg=TEXT_COLOR, bg=CARD_COLOR, font=("Arial", 11))

def create_entry(frame, show=None):
    return tk.Entry(frame, show=show, width=28, font=("Arial", 11), bd=1, relief="solid")

# -------------------- Login Frame --------------------
login_frame = tk.Frame(root, bg=CARD_COLOR, bd=2, relief="groove")
login_frame.pack(pady=40, padx=20, ipadx=10, ipady=10)

tk.Label(login_frame, text="Login", font=("Arial", 22, "bold"), fg="black", bg=CARD_COLOR).pack(pady=20)

create_label(login_frame, "Username").pack()
login_username = create_entry(login_frame)
login_username.pack(pady=5)

create_label(login_frame, "Password").pack()
login_password = create_entry(login_frame, show="*")
login_password.pack(pady=5)

tk.Button(login_frame, text="Login", command=login_user, bg=BUTTON_COLOR, fg="black",
          width=20, height=2, bd=0, font=("Arial", 11, "bold")).pack(pady=20)

tk.Label(login_frame, text="Don't have an account?", bg=CARD_COLOR, fg=TEXT_COLOR).pack()
tk.Button(login_frame, text="Register", command=switch_to_register, bg="#6BCB77", fg="black",
          width=15, height=1, bd=0, font=("Arial", 10, "bold")).pack(pady=5)

# -------------------- Registration Frame --------------------
register_frame = tk.Frame(root, bg=CARD_COLOR, bd=2, relief="groove")

tk.Label(register_frame, text="Register", font=("Arial", 22, "bold"), fg=BUTTON_COLOR, bg=CARD_COLOR).pack(pady=10)

for label_text, var_name in [
    ("First Name", "entry_first_name"),
    ("Last Name", "entry_last_name"),
    ("Email", "entry_email"),
    ("Username", "entry_username"),
    ("Password", "entry_password"),
    ("Phone Number", "entry_phone")
]:
    create_label(register_frame, label_text).pack()
    if label_text == "Password":
        entry = create_entry(register_frame, show="*")
    else:
        entry = create_entry(register_frame)
    entry.pack(pady=5)
    globals()[var_name] = entry

tk.Button(register_frame, text="Submit", command=register_user, bg="#6BCB77", fg="black",
          width=20, height=2, bd=0, font=("Arial", 11, "bold")).pack(pady=15)
tk.Button(register_frame, text="Back to Login", command=switch_to_login, bg=BUTTON_COLOR, fg="black",
          width=20, height=2, bd=0, font=("Arial", 11, "bold")).pack()

root.mainloop()