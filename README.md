# 💊 SmartPharma+ — Pharmacy Management System

## 📌 Overview

SmartPharma+ is a Python-based pharmacy management system that uses **OCR (Optical Character Recognition)** to analyze handwritten prescriptions and automatically generate bills.
It combines **automation, inventory management, and email integration** into one easy-to-use desktop application.

---

## 🚀 Features

* 📷 **Prescription Scanning (OCR)**
  Extracts text from uploaded prescription images using EasyOCR

* 🔍 **Smart Medicine Matching**
  Matches medicines using fuzzy logic (handles spelling variations)

* 💊 **Alternative Suggestions**
  Suggests substitutes based on same salt if medicine is out of stock

* 🧾 **Automatic Bill Generation**
  Generates PDF bills using ReportLab

* 📧 **Email Integration**
  Sends bills directly to customer email

* 📊 **Admin Dashboard**

  * Add / Update / Delete medicines
  * View inventory
  * Monitor stock levels

* ⚠️ **Low Stock Alerts**
  Notifies when medicine stock is below threshold

* 🕒 **Purchase History**
  Stores user transaction history using SQLite

---

## 🛠️ Technologies Used

* **Python**
* **CustomTkinter** (GUI)
* **SQLite** (Database)
* **EasyOCR** (Text extraction)
* **ReportLab** (PDF generation)
* **smtplib** (Email sending)
* **PIL (Pillow)** (Image handling)

---

## 📂 Project Structure

```
SmartPharma/
│── main.py
│── login.py
│── database.py
│── bill.py
│── text_ocr.py
│── pharmacy.db
│── users.db
│── README.md
│── .gitignore
```

---

## ▶️ How to Run

### 1️⃣ Clone the repository

```
git clone https://github.com/sanjanachaudhari229-cpu/SmartPharma-.git
cd SmartPharma-
```

### 2️⃣ Install dependencies

```
pip install customtkinter easyocr reportlab pillow
```

### 3️⃣ Run the application

```
python login.py
```

---

## 🔐 Security Note

Sensitive data like email credentials should not be stored directly in code.
Use a `.env` file for better security.


---

## 🎯 Future Enhancements

* Barcode scanning for medicines
* Online payment integration
* Cloud database support
* Mobile app version

---

## 👩‍💻 Author

**Sanjana Chaudhari**

---

## ⭐ Acknowledgment

This project was developed as part of a learning initiative in Python and software development.

---
