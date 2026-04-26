from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black
from reportlab.lib.units import cm
from io import BytesIO
from django.core.mail import EmailMessage
from django.conf import settings


def generate_invoice_pdf(order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    green = HexColor("#0f6b3f")

    # ================= HEADER =================
    # Logo
    try:
        p.drawImage(
            "static/website/images/Black_logo.png",
            40, height - 80,
            width=120,
            preserveAspectRatio=True,
            mask='auto'
        )
    except:
        pass

    # Company Details (Right)
    p.setFont("Helvetica", 10)
    p.drawRightString(width - 40, height - 50, "OrganicHubX")
    p.drawRightString(width - 40, height - 65, "Fresh & Organic Products")
    p.drawRightString(width - 40, height - 80, "support@organichubx.com")

    # Green Line
    p.setStrokeColor(green)
    p.setLineWidth(2)
    p.line(40, height - 100, width - 40, height - 100)

    # ================= TITLE =================
    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(green)
    p.drawString(40, height - 140, "Invoice")

    # ================= ORDER DETAILS =================
    p.setFillColor(black)
    p.setFont("Helvetica-Bold", 11)
    p.drawString(40, height - 175, f"Order ID:")
    p.drawString(40, height - 195, f"Status:")
    p.drawString(40, height - 215, f"Date:")

    p.setFont("Helvetica", 11)
    p.drawString(120, height - 175, order.order_id)
    p.drawString(120, height - 195, order.status)
    p.drawString(120, height - 215, order.created_at.strftime("%d %b %Y"))

    # ================= TABLE HEADER =================
    y = height - 260

    p.setFillColor(green)
    p.rect(40, y, width - 80, 30, fill=1)

    p.setFillColor("white")
    p.setFont("Helvetica-Bold", 11)
    p.drawString(60, y + 9, "Product")
    p.drawString(260, y + 9, "Qty")
    p.drawString(330, y + 9, "Price")
    p.drawString(430, y + 9, "Total")

    # ================= TABLE ROWS =================
    p.setFillColor(black)
    p.setFont("Helvetica", 11)
    y -= 30

    for item in order.items.all():
        p.drawString(60, y + 10, item.product.name)
        p.drawString(260, y + 10, str(item.qty))
        p.drawString(330, y + 10, f"Rs.{item.price:.2f}")
        p.drawString(430, y + 10, f"Rs.{item.qty * item.price:.2f}")

        p.line(40, y, width - 40, y)
        y -= 30

    # ================= TOTAL =================
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawRightString(width - 40, y + 30, "Total Paid:")

    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(green)
    p.drawRightString(width - 40, y, f"Rs.{order.total_amount:.2f}")

    # ================= FOOTER =================
    p.setFillColor(black)
    p.setFont("Helvetica", 10)
    p.line(40, 90, width - 40, 90)

    p.drawCentredString(
        width / 2,
        65,
        "Thank you for shopping with OrganicHubX"
    )
    p.drawCentredString(
        width / 2,
        50,
        "This is a system-generated invoice."
    )

    # ================= SAVE =================
    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer

def send_order_email(order, pdf_buffer):
    subject = f"Order Placed Successfully - {order.order_id}"

    message = f"""
Hi {order.user.first_name},

Thank you for shopping with OrganicHubX 🌱

Your order has been successfully placed.
Order ID: {order.order_id}
Total Paid: ₹{order.total_amount}

Please find your invoice attached.

Warm regards,
OrganicHubX Team
"""

    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
    )

    email.attach(
        f"Invoice_{order.order_id}.pdf",
        pdf_buffer.getvalue(),
        "application/pdf"
    )

    email.send()