# src/order_utils.py
from fpdf import FPDF
import csv
from datetime import datetime
import os

def save_order_to_csv(cart, products, orders_file="order_history.csv"):
    file_exists = os.path.isfile(orders_file)
    with open(orders_file, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "product", "quantity", "price"])
        if not file_exists:
            writer.writeheader()
        for product_key, quantity in cart.items():
            product = products[product_key]
            writer.writerow({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "product": product["name"],
                "quantity": quantity,
                "price": product["price"]
            })


def generate_invoice_pdf(cart, products, filename="invoice.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="D.Watson - Invoice", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(10)

    total = 0
    pdf.cell(40, 10, "Product", 1)
    pdf.cell(30, 10, "Qty", 1)
    pdf.cell(40, 10, "Price", 1)
    pdf.cell(40, 10, "Total", 1)
    pdf.ln()

    for item, qty in cart.items():
        name = products[item]["name"]
        price = products[item]["price"]
        line_total = price * qty
        total += line_total

        pdf.cell(40, 10, name[:15], 1)
        pdf.cell(30, 10, str(qty), 1)
        pdf.cell(40, 10, f"Rs.{price}", 1)
        pdf.cell(40, 10, f"Rs.{line_total}", 1)
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, f"Grand Total: Rs.{total}", ln=True)

    pdf.output(filename)
