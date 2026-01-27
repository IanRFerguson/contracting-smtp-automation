from datetime import datetime

import pytz
import resend

from utilities import application_logger

##########


def generate_email_body(
    addressee_first_name: str, client_name: str, days_back: int
) -> str:
    """
    Generates the HTML body for the email.

    Args:
        addressee_first_name (str): First name of the email recipient.
        client_name (str): Name of the client.
        days_back (int): Number of days back the report covers.

    Returns:
        str: The HTML body of the email.
    """

    body = f"""
    Hi {addressee_first_name},
    <br><br>
    I hope you're well! 
    <br><br>
    Please see attached for my <b>{client_name}</b> hours from the last {days_back} days.
    <br><br>
    If you have any questions or concerns please <a href='mailto:IAN@ianferguson.dev'>contact me at my monitored inbox</a>.
    <br><br>
    Thanks a bunch,
    <br>
    Ian Ferguson
    """

    return body


def send_email_with_resend(
    pdf_path: str,
    csv_path: str,
    days_back: int,
    addressee_first_name: str,
    addressee_email: str,
    client_name: str,
) -> None:
    """
    Sends an email with attachments using the Resend service.

    Args:
        pdf_path (str): Path to the PDF invoice file.
        csv_path (str): Path to the CSV hours file.
        days_back (int): Number of days back the report covers.
        addressee_first_name (str): First name of the email recipient.
        addressee_email (str): Email address of the recipient.
        client_name (str): Name of the client.
    """

    html_body = generate_email_body(
        addressee_first_name=addressee_first_name,
        client_name=client_name,
        days_back=days_back,
    )

    csv_file: bytes = open(csv_path, "rb").read()
    csv_attachment: resend.Attachment = {
        "content": list(csv_file),
        "filename": "hours.csv",
    }

    invoice_file: bytes = open(pdf_path, "rb").read()
    invoice_attachment: resend.Attachment = {
        "content": list(invoice_file),
        "filename": "invoice.pdf",
    }

    params: resend.Emails.SendParams = {
        "from": "Ian Ferguson Billing <no-reply@ianferguson.dev>",
        "to": [addressee_email],
        "subject": f"[AUTOMATED] Ferguson x {client_name} Hours - {datetime.now(tz=pytz.timezone('America/New_York')).strftime('%B %d, %Y')}",
        "html": html_body,
        "attachments": [csv_attachment, invoice_attachment],
    }

    resend.Emails.send(params=params)
