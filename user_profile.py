import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog

DB_FILE = "musicApp.db"

# ----------------- Database Functions -----------------
def get_current_user():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.user_id, u.first_name, u.last_name, u.email, u.username, u.phone_no, u.profile_pic
        FROM current_user cu
        JOIN users u ON cu.user_id = u.user_id
    """)
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "email": user[3],
            "username": user[4],
            "phone_no": user[5],
            "profile_pic": user[6]
        }
    return None

def update_user_profile(user_id, first_name, last_name, email, phone_no, profile_pic):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET first_name = ?, last_name = ?, email = ?, phone_no = ?, profile_pic = ?
        WHERE user_id = ?
    """, (first_name, last_name, email, phone_no, profile_pic, user_id))
    conn.commit()
    conn.close()
    return True

# ----------------- GUI -----------------
class UserProfileGUI:
    def __init__(self, root, user):
        self.user = user
        root.title("User Profile")
        root.attributes('-fullscreen', True)
        root.config(bg="white")  # make entire window white

        # --- Profile Frame ---
        frame = tk.Frame(root, padx=50, pady=50, bg="white")
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="User Profile", font=("Arial", 24, "bold"), bg="white", fg="black").pack(pady=20)

        # First Name
        tk.Label(frame, text="First Name:", font=("Arial", 16), bg="white", fg="black").pack(anchor="w")
        self.first_name_entry = tk.Entry(frame, font=("Arial", 16), bg="white", fg="black", insertbackground="black")
        self.first_name_entry.pack(fill="x", pady=10)
        self.first_name_entry.insert(0, user["first_name"] or "")

        # Last Name
        tk.Label(frame, text="Last Name:", font=("Arial", 16), bg="white", fg="black").pack(anchor="w")
        self.last_name_entry = tk.Entry(frame, font=("Arial", 16), bg="white", fg="black", insertbackground="black")
        self.last_name_entry.pack(fill="x", pady=10)
        self.last_name_entry.insert(0, user["last_name"] or "")

        # Email
        tk.Label(frame, text="Email:", font=("Arial", 16), bg="white", fg="black").pack(anchor="w")
        self.email_entry = tk.Entry(frame, font=("Arial", 16), bg="white", fg="black", insertbackground="black")
        self.email_entry.pack(fill="x", pady=10)
        self.email_entry.insert(0, user["email"] or "")

        # Phone Number
        tk.Label(frame, text="Phone Number:", font=("Arial", 16), bg="white", fg="black").pack(anchor="w")
        self.phone_entry = tk.Entry(frame, font=("Arial", 16), bg="white", fg="black", insertbackground="black")
        self.phone_entry.pack(fill="x", pady=10)
        self.phone_entry.insert(0, user["phone_no"] or "")

        # Profile Picture
        tk.Label(frame, text="Profile Picture:", font=("Arial", 16), bg="white", fg="black").pack(anchor="w")
        self.profile_pic_var = tk.StringVar()
        self.profile_pic_var.set(user["profile_pic"] or "")
        profile_frame = tk.Frame(frame, bg="white")
        profile_frame.pack(fill="x", pady=10)
        tk.Entry(profile_frame, textvariable=self.profile_pic_var, font=("Arial", 16), bg="white", fg="black", insertbackground="black").pack(side="left", fill="x", expand=True)
        tk.Button(profile_frame, text="Browse", font=("Arial", 14), bg="white", fg="black", relief="flat", command=self.browse_picture).pack(side="left", padx=5)

        # Save Button
        tk.Button(frame, text="Save Changes", bg="white", fg="black", font=("Arial", 16, "bold"),
                  relief="flat", command=self.save_changes).pack(pady=30)

        # Exit full screen with ESC
        root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

    def browse_picture(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", ("*.png", "*.jpg", "*.jpeg", "*.gif"))]
        )
        if filename:
            self.profile_pic_var.set(filename)


    def save_changes(self):
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone_no = self.phone_entry.get().strip()
        profile_pic = self.profile_pic_var.get().strip()

        update_user_profile(self.user["id"], first_name, last_name, email, phone_no, profile_pic)
        messagebox.showinfo("Success", "Profile updated successfully!")

# ----------------- Run GUI -----------------
if __name__ == "__main__":
    current_user = get_current_user()
    if not current_user:
        tk.messagebox.showerror("Error", "No user logged in!")
        exit()

    root = tk.Tk()
    app = UserProfileGUI(root, current_user)
    root.mainloop()
