import customtkinter as ctk
from tkinter import filedialog, messagebox
import sqlite3
from reportlab.pdfgen import canvas
import smtplib
from email.message import EmailMessage
import easyocr
from difflib import get_close_matches
import threading
from PIL import Image, ImageTk   
from bill import create_bill
from dotenv import load_dotenv
import os

load_dotenv()

reader = easyocr.Reader(['en'])

app = None
email_entry = None
loading_window = None

selected_image_path = None   
preview_label = None         


def init_history_table():
    conn = sqlite3.connect("pharmacy.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            medicines TEXT,
            total REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def send_email(receiver_email):
    sender_email = os.getenv("EMAIL_USER")
    app_password = os.getenv("EMAIL_PASS")

    msg = EmailMessage()
    msg['Subject'] = "Pharmacy Bill"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content("Attached bill")

    with open("new_bill.pdf", "rb") as f:
        msg.add_attachment(f.read(), maintype='application',
                           subtype='pdf', filename='bill.pdf')

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
    except:
        pass

def extract_text(path):
    result = reader.readtext(path)
    return " ".join([r[1] for r in result]).lower()

def get_medicines():
    conn = sqlite3.connect("pharmacy.db")
    cur = conn.cursor()
    cur.execute("SELECT name FROM medicines")
    data = cur.fetchall()
    conn.close()
    return [d[0] for d in data]

def get_alternatives(med_name):
    conn = sqlite3.connect("pharmacy.db")
    cur = conn.cursor()

   
    cur.execute("SELECT salt FROM medicines WHERE name=?", (med_name,))
    result = cur.fetchone()

    if not result:
        conn.close()
        return []

    salt = result[0]

   
    cur.execute("""
        SELECT name, stock, price
        FROM medicines
        WHERE salt=? AND stock > 0 AND name != ?
    """, (salt, med_name))

    data = cur.fetchall()
    conn.close()

    return data 

def match(word, med_list):
    m = get_close_matches(word, med_list, n=1, cutoff=0.6)
    return m[0] if m else None

def check(name):
    conn = sqlite3.connect("pharmacy.db")
    cur = conn.cursor()
    cur.execute("SELECT stock, price FROM medicines WHERE name=?", (name,))
    res = cur.fetchone()
    conn.close()
    return (True, res[1]) if res and res[0] > 0 else (False, 0)

def save_history(email, medicines, total):
    conn = sqlite3.connect("pharmacy.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO history (email, medicines, total)
        VALUES (?, ?, ?)
    """, (email, ", ".join(medicines), total))

    conn.commit()
    conn.close()


def show_loading():
    global loading_window, loading_bar

    loading_window = ctk.CTkToplevel(app)
    loading_window.geometry("300x180")
    loading_window.title("Processing")

    loading_window.update_idletasks()

    x = (loading_window.winfo_screenwidth() // 2) - 150
    y = (loading_window.winfo_screenheight() // 2) - 90
    loading_window.geometry(f"300x180+{x}+{y}")

    ctk.CTkLabel(
        loading_window,
        text="Analyzing Prescription...",
        font=("Arial", 15)
    ).pack(pady=20)

    loading_bar = ctk.CTkProgressBar(loading_window)
    loading_bar.pack(pady=20)
    loading_bar.start()

    loading_window.grab_set()

def hide_loading():
    global loading_window

    if loading_window is not None:
        try:
            loading_bar.stop()
            loading_window.destroy()
        except:
            pass
        loading_window = None


def process_file(file):
    text = extract_text(file)
    words = text.split()

    meds_list = get_medicines()

    matched = list(set([
        match(w, meds_list)
        for w in words
        if match(w, meds_list)
    ]))

    available = []
    total = 0

    for m in matched:
        ok, price = check(m)

        if ok:
           available.append((m, price))
           total += price

        else:
        
            alts = get_alternatives(m)

            print("Alternatives for", m, ":", alts)
            if not ok:
                   alts = get_alternatives(m)

            if alts:
                alt_names = [a[0] for a in alts]

                messagebox.showinfo(
                        "Alternative Available",
                         f"{m} is out of stock.\n\nAlternatives:\n{', '.join(alt_names)}"
     )
    
    available_names = [m for m, p in available]
    unavailable_names = list(set(matched) - set(available_names))

    messagebox.showinfo(
        "Result",
        f"Available: {available_names}\nNot Available: {unavailable_names}"
    )

    if available_names:
        proceed = messagebox.askyesno("Confirm", "Generate bill?")

        if proceed:
            create_bill(available, email_entry.get())

            email = email_entry.get()
            if email:
                send_email(email)

            # ✅ SAVE HISTORY
            save_history(email, available_names, total)

            messagebox.showinfo("Success", "Bill & Email sent")
        else:
            messagebox.showinfo("Cancelled", "Cancelled")

    app.after(0, hide_loading)

def upload():
    file = filedialog.askopenfilename()
    if file:
        show_loading()
        threading.Thread(
            target=process_file,
              args=(file,),
              daemon=True
            ).start()


def show_user_history():
    try:
        for widget in app.winfo_children():
            widget.destroy()

        win = app
        win.geometry("600x400")
        win.title("My History")

        email = email_entry.get().strip()

        if not email:
            messagebox.showerror("Error", "Please enter email first")
            win.destroy()
            return

        box = ctk.CTkTextbox(win, width=550, height=350)
        box.pack(pady=20)

        conn = sqlite3.connect("pharmacy.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT medicines, total, date 
            FROM history 
            WHERE email=?
        """, (email,))

        data = cur.fetchall()
        conn.close()

        if not data:
            box.insert("end", "No history found")
            return

        for d in data:
            box.insert("end", f"{d[0]} | Rs {d[1]} | {d[2]}\n\n")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ---------------- ADMIN FUNCTIONS -----------------

def refresh_medicine_table(box):
    box.delete('1.0', 'end')

    conn = sqlite3.connect('pharmacy.db')
    cur = conn.cursor()

    cur.execute('SELECT name, salt, stock, price FROM medicines ORDER BY name')
    rows = cur.fetchall()
    conn.close()

    box.insert('end', 'Medicine'.ljust(20))
    box.insert('end', 'Salt'.ljust(20))
    box.insert('end', 'Stock'.ljust(10))
    box.insert('end', 'Price\n')
    box.insert('end', '-'*60 + '\n')

    for r in rows:
        box.insert('end', str(r[0]).ljust(20))
        box.insert('end', str(r[1]).ljust(20))
        box.insert('end', str(r[2]).ljust(10))
        box.insert('end', f'Rs {r[3]}\n')


def add_medicine_admin(name_entry, salt_entry, stock_entry, price_entry, box):
    try:
        name = name_entry.get().strip()
        salt = salt_entry.get().strip()
        stock = int(stock_entry.get().strip())
        price = float(price_entry.get().strip())

        conn = sqlite3.connect('pharmacy.db')
        cur = conn.cursor()

        cur.execute(
            'INSERT INTO medicines (name, salt, stock, price) VALUES (?, ?, ?, ?)',
            (name, salt, stock, price)
        )

        conn.commit()
        conn.close()

        refresh_medicine_table(box)
        messagebox.showinfo('Success', 'Medicine added')

    except Exception as e:
        messagebox.showerror('Error', str(e))


def update_stock_admin(name_entry, stock_entry, box):
    try:
        name = name_entry.get().strip()
        stock = int(stock_entry.get().strip())

        conn = sqlite3.connect('pharmacy.db')
        cur = conn.cursor()

        cur.execute(
            'UPDATE medicines SET stock=? WHERE name=?',
            (stock, name)
        )

        conn.commit()
        conn.close()

        refresh_medicine_table(box)
        messagebox.showinfo('Success', 'Stock updated')

    except Exception as e:
        messagebox.showerror('Error', str(e))


def delete_medicine_admin(name_entry, box):
    try:
        name = name_entry.get().strip()

        conn = sqlite3.connect('pharmacy.db')
        cur = conn.cursor()

        cur.execute(
            'DELETE FROM medicines WHERE name=?',
            (name,)
        )

        conn.commit()
        conn.close()

        refresh_medicine_table(box)
        messagebox.showinfo('Success', 'Medicine deleted')

    except Exception as e:
        messagebox.showerror('Error', str(e))


def show_low_stock():
    conn = sqlite3.connect('pharmacy.db')
    cur = conn.cursor()

    cur.execute(
        'SELECT name, stock FROM medicines WHERE stock < 10'
    )

    rows = cur.fetchall()
    conn.close()

    if not rows:
        messagebox.showinfo('Low Stock', 'No low stock medicines')
        return

    msg = ''
    for r in rows:
        msg += f'{r[0]} : {r[1]} left\n'

    messagebox.showwarning('Low Stock Alert', msg)

def display_medicines(box):
    box.delete('1.0', 'end')

    # Monospace font for perfect alignment
    box.configure(font=("Courier New", 13))

    conn = sqlite3.connect('pharmacy.db')
    cur = conn.cursor()

    cur.execute("SELECT name, salt, stock, price FROM medicines ORDER BY name")
    rows = cur.fetchall()
    conn.close()

    # Header
    header = f"{'Medicine':<25}{'Salt':<25}{'Stock':<10}{'Price':<10}\n"
    box.insert('end', header)
    box.insert('end', "-" * 75 + "\n")

    # Rows
    for name, salt, stock, price in rows:
        line = f"{name:<25}{salt:<25}{stock:<10}{'Rs ' + str(price):<10}\n"
        box.insert('end', line)


def show_admin_panel():
    global app

    # ✅ clear screen
    for widget in app.winfo_children():
        widget.destroy()

    win = app
    win.geometry('1100x650')
    win.title('Admin Dashboard')

    # ===== TITLE =====
    ctk.CTkLabel(
        win,
        text='SmartPharma Admin Dashboard',
        font=('Segoe UI', 28, 'bold')
    ).pack(pady=15)

    # ===== MAIN CONTAINER =====
    main_container = ctk.CTkFrame(win, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=20, pady=10)

    # ===== TABLE CARD (CREATE FIRST ✅) =====
    table_card = ctk.CTkFrame(main_container, corner_radius=15)
    table_card.pack(fill="both", expand=True, pady=10)

    ctk.CTkLabel(
        table_card,
        text="Medicine Inventory",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    table_box = ctk.CTkTextbox(table_card)
    table_box.pack(fill="both", expand=True, padx=10, pady=10)

    # ===== TOP CARD =====
    top_card = ctk.CTkFrame(main_container, corner_radius=15)
    top_card.pack(fill="x", pady=10)

    form_frame = ctk.CTkFrame(top_card, fg_color="transparent")
    form_frame.pack(pady=15)

    name_entry = ctk.CTkEntry(form_frame, placeholder_text='Medicine Name', width=180)
    name_entry.grid(row=0, column=0, padx=10)

    salt_entry = ctk.CTkEntry(form_frame, placeholder_text='Salt', width=180)
    salt_entry.grid(row=0, column=1, padx=10)

    stock_entry = ctk.CTkEntry(form_frame, placeholder_text='Stock', width=120)
    stock_entry.grid(row=0, column=2, padx=10)

    price_entry = ctk.CTkEntry(form_frame, placeholder_text='Price', width=120)
    price_entry.grid(row=0, column=3, padx=10)

    # ===== BUTTONS =====
    button_frame = ctk.CTkFrame(top_card, fg_color="transparent")
    button_frame.pack(pady=10)

    # ADD
    ctk.CTkButton(
        button_frame,
        text='Add',
        width=120,
        fg_color="#2ecc71",
        command=lambda: [
            add_medicine_admin(name_entry, salt_entry, stock_entry, price_entry, table_box),
            display_medicines(table_box)
        ]
    ).grid(row=0, column=0, padx=10)

    # UPDATE
    ctk.CTkButton(
        button_frame,
        text='Update',
        width=120,
        fg_color="#f39c12",
        command=lambda: [
            update_stock_admin(name_entry, stock_entry, table_box),
            display_medicines(table_box)
        ]
    ).grid(row=0, column=1, padx=10)

    # DELETE
    ctk.CTkButton(
        button_frame,
        text='Delete',
        width=120,
        fg_color="#e74c3c",
        command=lambda: [
            delete_medicine_admin(name_entry, table_box),
            display_medicines(table_box)
        ]
    ).grid(row=0, column=2, padx=10)

    # LOW STOCK
    ctk.CTkButton(
        button_frame,
        text='Low Stock',
        width=140,
        command=show_low_stock
    ).grid(row=0, column=3, padx=10)

    # REFRESH
    ctk.CTkButton(
        button_frame,
        text='Refresh',
        width=120,
        command=lambda: display_medicines(table_box)
    ).grid(row=0, column=4, padx=10)

    # ===== BACK BUTTON (VERY IMPORTANT) =====
    ctk.CTkButton(
        win,
        text="⬅ Back",
        command=lambda: run_main_app(app, "Admin")
    ).pack(pady=10)

    # INITIAL LOAD
    display_medicines(table_box)



def run_main_app(root,role):
    global app,email_entry, preview_label

    app = root

    for widget in app.winfo_children():
        widget.destroy()

    init_history_table()

    app.geometry("900x600")
    app.title("SmartPharma+")
    ctk.set_appearance_mode("light")

   
    main_frame = ctk.CTkFrame(app, fg_color="transparent")
    main_frame.pack(expand=True)

    
    wrapper = ctk.CTkFrame(app, fg_color="transparent")
    wrapper.pack(expand=True)

    
    card = ctk.CTkFrame(
        wrapper,
        width=500,
        height=520,
        corner_radius=20,
        fg_color="#ffffff"
    )
    card.pack(pady=20)
    card.pack_propagate(False)

    
    ctk.CTkLabel(
        card,
        text="SmartPharma+",
        font=("Segoe UI", 30, "bold"),
        text_color="#2f4f2f"
    ).pack(pady=(30, 10))

    ctk.CTkLabel(
        card,
        text=" Prescription Analyzer",
        font=("Segoe UI", 14),
        text_color="gray40"
    ).pack(pady=(0, 20))

    
    email_entry = ctk.CTkEntry(
        card,
        placeholder_text="Enter receiver's email (example@gmail.com)",
        width=380,
        height=42,
        font=("Arial", 13)
    )
    email_entry.pack(pady=15)

    
    ctk.CTkButton(
        card,
        text="Upload Prescription",
        fg_color="#2e5d34",
        hover_color="#244a2a",
        width=220,
        height=42,
        font=("Segoe UI", 13, "bold"),
        command=upload
    ).pack(pady=15)

   
    preview_label = ctk.CTkLabel(
        card,
        text="No Prescription Selected",
        font=("Segoe UI", 12),
        text_color="gray50"
    )
    preview_label.pack(pady=10)

    
    def select_image():
        global selected_image_path, preview_label

        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )

        if file_path:
            selected_image_path = file_path

            img = Image.open(file_path)
            img = img.resize((180, 180))
            img_tk = ImageTk.PhotoImage(img)

            preview_label.configure(image=img_tk, text="")
            preview_label.image = img_tk

    
    ctk.CTkButton(
        card,
        text="Preview Image",
        fg_color="#3d4f1f",
        hover_color="#2f3d17",
        width=180,
        height=35,
        font=("Segoe UI", 12),
        command=select_image
     ).pack(pady=10)
    
    if role == "User":
     ctk.CTkButton(
       main_frame,
       text="My History",
       fg_color="#3d4f1f",
       hover_color="#2f3d17",
       width=200,
       height=40,
       command=show_user_history
    ).pack(pady=10)

    if role == "Admin":
     ctk.CTkButton(
       main_frame,
       text="Admin Panel",
       fg_color="#3d4f1f",
       hover_color="#2f3d17",
       width=200,
       height=40,
       command=show_admin_panel
    ).pack(pady=10)
    
    ctk.CTkLabel(
        card,
        text="Powered by OCR Matching System",
        font=("Segoe UI", 11),
        text_color="gray60"
    ).pack(pady=(20, 10))


 

    