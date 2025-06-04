import os
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

##########


def generate_html_body(
    addressee_first_name: str, client_name: str, days_back: int
) -> str:
    body = f"""
    Hi {addressee_first_name},
    <br><br>
    I hope you're well! Please see attached for my {client_name} hours for the last {days_back} days.
    <br><br>
    If you have any questions or concerns please <a href='mailto:IANFERGUSONRVA@gmail.com'>contact me at my monitored inbox</a>.
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
    Creates the message to be sent, including
    * Subject
    * To / From addresses
    * HTML email body
    * Attached CSV file
    """

    msg = MIMEMultipart("mixed")

    # Message metadata
    msg["From"] = sender_email
    msg["To"] = addressee_email
    msg["Subject"] = (
        f"[AUTOMATED] Ferguson x {client_name} Hours - {datetime.now().strftime('%B %d, %Y')}"
    )

    # Create and attach email body
    body_text = MIMEText(
        generate_html_body(
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
