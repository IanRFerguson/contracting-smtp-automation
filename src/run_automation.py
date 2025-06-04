import os
import sys
from smtplib import SMTP
from typing import Union

from google.cloud import bigquery
from pandas import DataFrame

from email_helpers import generate_multipart_message
from utilities import generate_attachment_naming_convention, logger

##########

"""
NOTE - This program assumes that your hours are in a template with
the following headings - `Period, Day, Hours, Category, Purpose, Accomplished`

TODO - This could be reconfigured to take a dynamic list of headers
"""


def get_contracting_hours(
    table_name: str, bq: bigquery.Client, days_back: int
) -> Union[DataFrame, None]:
    """
    Reads in data from BigQuery and filters out to the last week.
    If there are no records in the last 7 days we'll return `None` instead
    of a Polars Table
    """

    logger.info(f"Reading hours from {table_name}...")
    job = bq.query(
        f"SELECT * FROM {table_name} WHERE DATE_DIFF(CURRENT_DATE(), CAST(Day as DATE), DAY) < {days_back}"
    )
    resp = [row.values() for row in job.result()]

    return DataFrame(
        resp, columns=["Period", "Day", "Hours", "Category", "Purpose", "Accomplished"]
    )


def send_email(
    tbl: DataFrame,
    addressee_email: str,
    addressee_first_name: str,
    client_name: str,
    days_back: int,
    smtp: SMTP,
    smtp_creds: dict,
) -> None:
    """
    Formats and attaches CSV to the body of an outgoing email
    to the client address.
    """

    # Save file locally
    filename = generate_attachment_naming_convention(
        days_back=days_back, client_name=client_name
    )
    logger.debug(f"Writing output to {filename}")
    tbl.to_csv(f"./{filename}")

    email_body = generate_multipart_message(
        sender_email=smtp_creds["user"],
        addressee_first_name=addressee_first_name,
        addressee_email=addressee_email,
        days_back=days_back,
        client_name=client_name,
        attachment_filename=filename,
    )

    # Send message
    with smtp as server:
        server.ehlo()
        server.starttls()
        server.login(**smtp_creds)

        logger.info(f"Sending to {addressee_first_name} @ {addressee_email}...")
        server.sendmail(
            from_addr="noreply@ianferguson.dev",
            to_addrs=addressee_email,
            msg=email_body.as_string(),
        )
        logger.info("Successfully sent")


def run(
    table_name: str,
    addressee_first_name: str,
    addressee_email: str,
    client_name: str,
    days_back: int,
    bq: bigquery.Client,
    smtp: SMTP,
    smtp_creds: dict,
):
    # Check to see if there are any contracting hours in the last week
    hours_this_week = get_contracting_hours(
        table_name=table_name, bq=bq, days_back=days_back
    )

    # If not, exit the program
    if hours_this_week.empty:
        logger.info("No hours to report for this time period")
        sys.exit(0)

    send_email(
        tbl=hours_this_week,
        addressee_email=addressee_email,
        addressee_first_name=addressee_first_name,
        client_name=client_name,
        smtp=smtp,
        smtp_creds=smtp_creds,
        days_back=days_back,
    )


#####

if __name__ == "__main__":
    SOURCE_TABLE_NAME = os.environ["TABLE_NAME"]
    ADDRESSEE_FIRST_NAME = os.environ["ADDRESSEE_FIRST_NAME"]
    ADDRESSEE_EMAIL = os.environ["ADDRESSEE_EMAIL"]
    CLIENT_NAME = os.environ["CLIENT_NAME"]
    DAYS_BACK = os.environ.get("DAYS_BACK", 7)

    BIGQUERY_CLIENT = bigquery.Client(
        client_options={
            "scopes": [
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/bigquery",
                "https://www.googleapis.com/auth/cloud-platform",
            ]
        }
    )
    SMTP_CLIENT = SMTP(host="smtp.gmail.com", port=587)
    SMTP_CREDS = {
        "user": os.environ["SMTP_USERNAME"],
        "password": os.environ["SMTP_PASSWORD"],
    }

    run(
        table_name=SOURCE_TABLE_NAME,
        addressee_first_name=ADDRESSEE_FIRST_NAME,
        addressee_email=ADDRESSEE_EMAIL,
        client_name=CLIENT_NAME,
        days_back=DAYS_BACK,
        bq=BIGQUERY_CLIENT,
        smtp=SMTP_CLIENT,
        smtp_creds=SMTP_CREDS,
    )
