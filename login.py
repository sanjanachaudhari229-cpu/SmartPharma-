import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import main   
import re
from tkinter import messagebox

def is_valid_gmail(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@gmail\.com$"
    return re.match(pattern, email) is not None 

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.geometry("520x600")
app.title("Smart Pharmacy Login")

# DB
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT,
    password TEXT,
    role TEXT
)
""")
conn.commit()

login_role = ctk.StringVar(value="User")
register_role = ctk.StringVar(value="User")



def login_user():
    email = login_email.get().strip()
    password = login_password.get().strip()
    role = login_role.get()
 
    if not is_valid_gmail(email):
        messagebox.showerror("Error", "Only Gmail accounts (@gmail.com) allowed")
        return

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=? AND role=?",
        (email, password, role)


    )

    if cursor.fetchone():
        messagebox.showinfo("Success", "Login Successful")

        login_frame.pack_forget()
        main.run_main_app(app,role)   # ✅ FIXED (NO subprocess)

    else:
        messagebox.showerror("Error", "Invalid login")



def register_user():
    email = reg_email.get().strip()
    password = reg_password.get().strip()
    role = register_role.get()

    if not is_valid_gmail(email):
        messagebox.showerror("Error", "Only Gmail accounts (@gmail.com) allowed")
        return

    cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (email, password, role))
    conn.commit()

    messagebox.showinfo("Success", "Registered Successfully")
    show_login()


def show_register():
    login_frame.pack_forget()
    register_frame.pack(expand=True)


def show_login():
    register_frame.pack_forget()
    login_frame.pack(expand=True)



login_frame = ctk.CTkFrame(
    app,
    corner_radius=20,
    fg_color="#F7F7F7"
)
login_frame.pack(expand=True, fill="both", padx=40, pady=40)


ctk.CTkLabel(
    login_frame,
    text="Login Page",
    font=("Arial", 30, "bold"),
    text_color="#556B2F"
).pack(pady=(40, 25))


login_email = ctk.CTkEntry(
    login_frame,
    placeholder_text="Enter Email Address",
    width=380,
    height=45,
    font=("Arial", 14),
    border_width=2,
    corner_radius=12
)
login_email.pack(pady=10)


login_password = ctk.CTkEntry(
    login_frame,
    placeholder_text="Enter Password",
    show="*",
    width=380,
    height=45,
    font=("Arial", 14),
    border_width=2,
    corner_radius=12
)
login_password.pack(pady=10)


ctk.CTkOptionMenu(
    login_frame,
    values=["User", "Admin"],
    variable=login_role,
    width=200,
    fg_color="#556B2F",
    button_color="#3d4f1f",
    button_hover_color="#2f3d17"
).pack(pady=15)


ctk.CTkButton(
    login_frame,
    text="Login",
    fg_color="#556B2F",
    hover_color="#3d4f1f",
    width=220,
    height=45,
    font=("Arial", 14, "bold"),
    corner_radius=12,
    command=login_user
).pack(pady=(20, 10))


ctk.CTkButton(
    login_frame,
    text="Create Account",
    fg_color="transparent",
    border_width=2,
    border_color="#556B2F",
    text_color="#556B2F",
    hover_color="#E8F0E3",
    width=220,
    height=40,
    font=("Arial", 13),
    corner_radius=12,
    command=show_register
).pack()


register_frame = ctk.CTkFrame(
    app,
    corner_radius=20,
    fg_color="#F7F7F7"
)

# Title
ctk.CTkLabel(
    register_frame,
    text="Registration Page",
    font=("Arial", 30, "bold"),
    text_color="#556B2F"
).pack(pady=(40, 25))


reg_email = ctk.CTkEntry(
    register_frame,
    placeholder_text="Enter Email Address",
    width=380,
    height=45,
    font=("Arial", 14),
    border_width=2,
    corner_radius=12
)
reg_email.pack(pady=10)


reg_password = ctk.CTkEntry(
    register_frame,
    placeholder_text="Enter Password",
    show="*",
    width=380,
    height=45,
    font=("Arial", 14),
    border_width=2,
    corner_radius=12
)
reg_password.pack(pady=10)


ctk.CTkOptionMenu(
    register_frame,
    values=["User", "Admin"],
    variable=register_role,
    width=200,
    fg_color="#556B2F",
    button_color="#3d4f1f",
    button_hover_color="#2f3d17"
).pack(pady=15)

ctk.CTkButton(
    register_frame,
    text="Register",
    fg_color="#556B2F",
    hover_color="#3d4f1f",
    width=220,
    height=45,
    font=("Arial", 14, "bold"),
    corner_radius=12,
    command=register_user
).pack(pady=(20, 10))


ctk.CTkButton(
    register_frame,
    text="Back to Login",
    fg_color="transparent",
    border_width=2,
    border_color="#556B2F",
    text_color="#556B2F",
    hover_color="#E8F0E3",
    width=220,
    height=40,
    font=("Arial", 13),
    corner_radius=12,
    command=show_login
).pack()
app.mainloop()