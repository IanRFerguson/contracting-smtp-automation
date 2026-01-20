import os
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

from utilities import application_logger, format_attachment_name

##########


def generate_email_body(addressee_first_name: str, client_name: str, days_back: int) -> str:
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
    Formats and attaches a zip file to the body of an outgoing email
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
    zip_file = format_attachment_name(days_back=days_back, client_name=client_name, assets_directory=assets_directory)

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

            if not addressee_email:
                raise ValueError("TEST_EMAIL_INBOX environment variable must be set in non-production environments.")

        application_logger.debug(f"Sending to {addressee_first_name} @ {addressee_email}...")
        try:
            server.sendmail(
                from_addr=from_address,
                to_addrs=addressee_email,
                msg=email_body.as_string(),
            )
            application_logger.debug("Successfully sent")

        except Exception as e:
            application_logger.error(f"Failed to send email: {e}")
