import os

import click
from google.cloud import bigquery, storage

from asset_helpers import build_attachments
from email_helpers import send_email_with_resend
from utilities import (
    application_logger,
    get_contracting_hours,
    get_data_for_environment,
    write_assets_to_gcs,
)

#####

# Initialize clients
BIGQUERY_CLIENT = bigquery.Client(
    client_options={
        "scopes": [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/bigquery",
            "https://www.googleapis.com/auth/cloud-platform",
        ]
    }
)
STORAGE_CLIENT = storage.Client()


@click.command()
@click.option(
    "--days-back",
    default=7,
    help="Number of days back to query for contracting hours.",
    type=int,
)
@click.option(
    "--bucket-name",
    default=os.environ.get("GCS_BUCKET_NAME"),
    help="GCS bucket name to upload email assets to.",
    type=str,
)
def main(days_back: int, bucket_name: str) -> None:
    """
    Entrypoint for the contracting hours email automation.

    This function performs the following operations:
    * Initializes BigQuery and SMTP clients.
    * Iterates over each consultant defined in the `CONSULTANT_MAP`.
    * Retrieves contracting hours from BigQuery for the specified number of days.
    * If hours are found, generates a CSV attachment and PDF invoice, zips them,  and composes an email.
    * Sends the email to the client's email address.

    Args:
        days_back (int): Number of days back to query for contracting hours.
        bucket_name (str): GCS bucket name to upload email assets to.
    """

    if not bucket_name:
        raise ValueError(
            "GCS bucket name must be provided via --bucket-name or env var."
        )

    CONSULTANT_MAP, GLOBAL_MAP = get_data_for_environment(
        is_prod_run=os.environ.get("STAGE") == "production",
        storage_client=STORAGE_CLIENT,
        bucket_name=bucket_name,
    )

    for client_name in CONSULTANT_MAP.keys():
        application_logger.info(f"* Processing client: {client_name}")

        # Query the database for contracting hours
        hours_this_week = get_contracting_hours(
            table_name=CONSULTANT_MAP[client_name]["table_name"],
            bq=BIGQUERY_CLIENT,
            days_back=days_back,
        )

        # If there are no hours, we can skip ahead
        if hours_this_week.empty:
            application_logger.warning(
                "* No contracting hours found for the specified period."
            )
            continue

        # Create the email assets, including a CSV attachment and invoice
        application_logger.info("** Generating email assets")
        csv_path, pdf_path = build_attachments(
            df=hours_this_week,
            days_back=days_back,
            global_map=GLOBAL_MAP,
            client_map=CONSULTANT_MAP[client_name],
        )

        # Email our contact
        application_logger.info("** Sending email to client")
        send_email_with_resend(
            csv_path=csv_path,
            pdf_path=pdf_path,
            days_back=days_back,
            addressee_first_name=CONSULTANT_MAP[client_name]["contact_name"].split(" ")[
                0
            ],
            addressee_email=CONSULTANT_MAP[client_name]["contact_email"],
            client_name=client_name,
        )

        # Upload assets to GCS for record-keeping
        application_logger.info("** Uploading assets to GCS")
        write_assets_to_gcs(
            csv_path=csv_path,
            pdf_path=pdf_path,
            client_name=client_name,
            storage_client=STORAGE_CLIENT,
            bucket_name=bucket_name,
        )


#####

if __name__ == "__main__":
    main()
