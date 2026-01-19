import os
from datetime import datetime, timedelta
from uuid import uuid4

import pytz
from jinja2 import Environment, FileSystemLoader
from pandas import DataFrame
from weasyprint import HTML

from color_logger import logger
from config import GLOBAL_MAP

#####

TODAY = datetime.now(tz=pytz.timezone("America/New_York"))


def templatize_html_to_pdf(
    output_path: str,
    invoice_no: str,
    client_name: str,
    billing_period: str,
    items: list[dict],
    hourly_rate: float,
    tax_rate: float = 0.0,
    payment_method: str = "Bank Transfer",
) -> str:
    """
    Renders the HTML template with provided data and converts it to a PDF invoice.

    Args:
        output_path (str): Path where the PDF should be saved.
        invoice_no (str): Invoice number.
        client_name (str): Name of the client being billed.
        billing_period (str): Billing period (e.g., "2025-01-01 to 2025-01-13").
        items (list[dict]): List of invoice items, each with keys: description, rate, qty, amount.
        hourly_rate (float): Hourly rate for the consultant.
        tax_rate (float): Tax rate as a percentage (default: 0.0).
        payment_method (str): Payment method description (default: "Bank Transfer").

    Returns:
        str: Path to the created PDF file.
    """

    # Aggregate hours by category (e.g., Admin, Troubleshooting, App Development)
    category_items = {}
    for item in items:
        if item["Category"].upper().strip() not in category_items:
            category_items[item["Category"].upper().strip()] = item["Hours"]
        else:
            category_items[item["Category"].upper().strip()] += item["Hours"]

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, "assets")

    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("base_attachment.html")

    # Calculate totals
    subtotal = sum(item["Hours"] for item in items) * hourly_rate
    total = subtotal * (1 + tax_rate / 100)

    # Prepare template context
    due_date = (TODAY + timedelta(days=30)).strftime("%b %d, %Y").upper()
    context = {
        "company_name": GLOBAL_MAP["name"],
        "address": f"{GLOBAL_MAP['address']}, {GLOBAL_MAP['city']}, {GLOBAL_MAP['state']} {GLOBAL_MAP['zip']}",
        "phone": GLOBAL_MAP["phone"],
        "email": GLOBAL_MAP["email"],
        "invoice_no": invoice_no,
        "hourly_rate": hourly_rate,
        "date": TODAY.strftime("%b %d, %Y").upper(),
        "billing_period": billing_period,
        "due_date": due_date,
        "client_name": client_name,
        "items": category_items,
        "total": total,
        "payment_method": payment_method,
    }

    # Render HTML
    html_content = template.render(**context)

    # Read CSS file
    css_path = os.path.join(template_dir, "style.css")

    # Convert to PDF
    HTML(string=html_content).write_pdf(output_path, stylesheets=[css_path])

    logger.debug(f"Generated invoice PDF at {output_path}")

    return output_path


def build_attachments(df: DataFrame, days_back: int, **kwargs) -> str:
    """
    Given a Pandas DataFrame, build the email attachments and return
    the directory where they are stored.

    Args:
        df (DataFrame): Pandas DataFrame containing contracting hours.
        days_back (int): Number of days back to include in the billing period.

    Returns:
        str: Directory path where attachments are stored.
    """

    output_dir = f"{os.path.abspath(os.getcwd())}/temp_attachments_{uuid4().hex}"
    logger.debug(f"Creating temporary directory at {output_dir}...")

    os.makedirs(output_dir, exist_ok=True)

    df.to_csv(f"{output_dir}/contracting_hours.csv", index=False)

    # Build invoice PDF
    billing_period_start = (TODAY - timedelta(days=days_back)).strftime("%b %d, %Y").upper()
    billing_period_end = TODAY.strftime("%b %d, %Y").upper()
    templatize_html_to_pdf(
        output_path=f"{output_dir}/invoice.pdf",
        invoice_no=f"INV-{TODAY.strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}",
        client_name=kwargs["billed_to"],
        billing_period=f"{billing_period_start} to {billing_period_end}",
        items=df.to_dict(orient="records"),
        hourly_rate=kwargs["hourly_rate"],
        payment_method=kwargs.get("payment_method", "Bank Transfer"),
    )

    return output_dir
