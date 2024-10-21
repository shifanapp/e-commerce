# utils.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_invoice_pdf(invoice):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, f"Invoice Number: {invoice.invoice_number}")
    c.drawString(100, 735, f"Date: {invoice.date}")
    c.drawString(100, 720, f"Customer: {invoice.customer.username}")
    c.drawString(100, 705, f"Total Amount: {invoice.total_amount}")
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
