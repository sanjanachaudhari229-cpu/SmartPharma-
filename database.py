import sqlite3

conn = sqlite3.connect("pharmacy.db")
cursor = conn.cursor()


cursor.execute("DROP TABLE IF EXISTS medicines")
cursor.execute("DROP TABLE IF EXISTS history")


cursor.execute("""
CREATE TABLE medicines (
    name TEXT,
    salt TEXT,
    stock INTEGER,
    price REAL
)
""")

cursor.execute("""
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    medicines TEXT,
    total REAL,
    date TEXT DEFAULT CURRENT_TIMESTAMP
)
""")


medicines_data = [
    ("paracetamol", "paracetamol", 10, 20),
    ("crocin", "paracetamol", 5, 30),
    ("dolo", "paracetamol", 0, 25),

    ("pantaprazole", "pantoprazole", 5, 55),
    ("pan40", "pantoprazole", 10, 60),

    ("aspirin", "aspirin", 8, 15),

    ("cetirizine", "cetirizine", 10, 30),
    ("okacet", "cetirizine", 9, 20),

    ("vitamin c", "vitamin c", 0, 40),
    ("celin", "vitamin c", 6, 35)
]

cursor.executemany(
    "INSERT INTO medicines (name, salt, stock, price) VALUES (?, ?, ?, ?)",
    medicines_data
)

conn.commit()
conn.close()

print("Database RESET & UPDATED successfully!")