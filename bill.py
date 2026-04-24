from reportlab.pdfgen import canvas
from datetime import datetime

def create_bill(medicines, email="User"):
    c = canvas.Canvas("new_bill.pdf")
    width, height = 600, 800

    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(170, 760, "SMART PHARMACY INVOICE")

    c.setFont("Helvetica", 11)
    c.drawString(50, 730, f"Customer: {email}")
    c.drawString(50, 710, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    c.line(50, 695, 550, 695)

   
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, 670, "Medicine")
    c.drawString(280, 670, "Price")

    c.line(50, 660, 550, 660)

    y = 640
    total = 0

    c.setFont("Helvetica", 11)

    for m in medicines:
        name = m[0]
        price = m[1]

        c.drawString(60, y, str(name))
        c.drawString(280, y, f"Rs {price}")

        total += price
        y -= 25

        
        if y < 80:
            c.showPage()
            y = 750

    c.line(50, y, 550, y)

    
    c.setFont("Helvetica-Bold", 13)
    c.drawString(280, y - 30, "TOTAL:")
    c.drawString(360, y - 30, f"Rs {total}")

    
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(180, 40, "Thank you for using SmartPharma+")

    c.save()

    print("Bill generated successfully!")