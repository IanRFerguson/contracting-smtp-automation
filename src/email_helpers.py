import os
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

from utilities import generate_attachment_naming_convention, logger

##########


def generate_email_body(addressee_first_name: str, client_name: str, days_back: int) -> str:
    body = f"""
    Hi {addressee_first_name},
    <br><br>
    I hope you're well! Please see attached for my {client_name} hours from the last {days_back} days.
    <br><br>
    If you have any questions or concerns please <a href='mailto:IAN@ianferguson.dev'>contact me at my monitored inbox</a>.
    <br><br>
    Thanks a bunch,
    <br>
    Ian Ferguson
    """

    return body


def generate_multipart_message(
    sender_email: str,
    addressee_first_name: str,
    addressee_email: str,
    days_back: int,
    client_name: str,
    attachment_filename: str,
) -> MIMEMultipart:
    """
    Generates a multipart email message with an attachment.

    Args:
        sender_email (str): Email address of the sender.
        addressee_first_name (str): First name of the email recipient.
        addressee_email (str): Email address of the recipient.
        days_back (int): Number of days back the report covers.
        client_name (str): Name of the client.
        attachment_filename (str): Path to the attachment file.

    Returns:
        MIMEMultipart: The constructed email message with attachment.
    """

    msg = MIMEMultipart("mixed")

    # Message metadata
    msg["From"] = sender_email
    msg["To"] = addressee_email
    msg["Subject"] = f"[AUTOMATED] Ferguson x {client_name} Hours - {datetime.now().strftime('%B %d, %Y')}"

    # Create and attach email body
    body_text = MIMEText(
        generate_email_body(
            addressee_first_name=addressee_first_name,
            client_name=client_name,
            days_back=days_back,
        ),
        "html",
    )
    msg.attach(body_text)

    # Read and attach CSV file
    with open(attachment_filename, "rb") as _fp:
        base_name = os.path.basename(attachment_filename)

        attachment = MIMEApplication(_fp.read(), Name=base_name)
        attachment["Content-Disposition"] = f'attachment; filename="{base_name}"'

        msg.attach(attachment)

    return msg


def send_email(
    assets_directory: str,
    smtp: SMTP,
    smtp_creds: dict,
    days_back: int,
    from_address: str,
    addressee_first_name: str,
    addressee_email: str,
    client_name: str,
) -> None:
    """
    Formats and attaches CSV to the body of an outgoing email
    to the client address.

    Args:
        assets_directory (str): Directory containing the email assets.
        smtp (SMTP): SMTP client instance.
        smtp_creds (dict): SMTP credentials dictionary with 'user' and 'password' keys.
        days_back (int): Number of days back the report covers.
        from_address (str): From address for outgoing emails.
        addressee_first_name (str): First name of the email recipient.
        addressee_email (str): Email address of the recipient.
        client_name (str): Name of the client.
    """

    # Save file locally
    zip_file = generate_attachment_naming_convention(
        days_back=days_back, client_name=client_name, assets_directory=assets_directory
    )

    email_body = generate_multipart_message(
        sender_email=smtp_creds["user"],
        addressee_first_name=addressee_first_name,
        addressee_email=addressee_email,
        days_back=days_back,
        client_name=client_name,
        attachment_filename=zip_file,
    )

    # Send message
    with smtp as server:
        server.ehlo()
        server.starttls()
        server.login(**smtp_creds)

        if os.environ.get("STAGE") != "production":
            addressee_email = os.environ.get("TEST_EMAIL_INBOX")

        logger.debug(f"Sending to {addressee_first_name} @ {addressee_email}...")
        server.sendmail(
            from_addr=from_address,
            to_addrs=addressee_email,
            msg=email_body.as_string(),
        )
        logger.debug("Successfully sent")
