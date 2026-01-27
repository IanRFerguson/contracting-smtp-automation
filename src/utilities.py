import json
import os
import shutil
from datetime import datetime, timedelta
from typing import Tuple, Union

import pytz
from google.cloud import bigquery, storage
from pandas import DataFrame

from color_logger import application_logger

#####


def format_attachment_name(days_back: int, client_name: str, assets_directory: str, suffix: str = ".zip") -> str:
    """
    Creates a zip file from the assets directory with a standardized naming convention
    and returns the path to the created zip file.

    Example - `FERGUSON_ACLU_hours__2025-01-01__2025-01-13.zip`

    Args:
        days_back (int): Number of days back the report covers.
        client_name (str): Name of the client.
        assets_directory (str): Directory containing the assets to be zipped.
        suffix (str): Suffix for the file (default: .zip).

    Returns:
        str: Path to the created zip file.
    """

    _today = datetime.now(pytz.timezone("America/New_York"))
    _preceding_boundary = _today - timedelta(days=days_back)

    _date_formatted = f"{_preceding_boundary.strftime('%Y-%m-%d')}__{_today.strftime('%Y-%m-%d')}"

    base_filename = f"FERGUSON_{client_name.upper().strip().replace(' ', '_')}_hours__{_date_formatted}"

    # Create zip file in the parent directory of assets_directory
    output_dir = os.path.dirname(assets_directory) or os.getcwd()
    output_base = os.path.join(output_dir, base_filename)

    # Create the zip file (shutil.make_archive adds .zip automatically)
    application_logger.debug(f"Creating zip archive at {output_base}{suffix}...")
    shutil.make_archive(output_base, "zip", assets_directory)

    return f"{output_base}{suffix}"


def get_contracting_hours(table_name: str, bq: bigquery.Client, days_back: int) -> Union[DataFrame, None]:
    """
    Reads in data from BigQuery and filters out to the last week.
    If there are no records in the last 7 days we'll return `None` instead
    of a Pandas DataFrame
    """

    application_logger.debug(f"Reading hours from {table_name}...")
    job = bq.query(
        f"""
        SELECT 
            * 
        FROM {table_name} 
        WHERE DATE_DIFF(CURRENT_DATE(), CAST(Day as DATE), DAY) < {days_back}
        ORDER BY Day DESC
        """
    )
    resp = [row.values() for row in job.result()]
    application_logger.debug(resp)

    if os.environ.get("STAGE") != "production":
        columns = ["Period", "Day", "Hours", "Category", "Accomplished"]
    else:
        columns = ["Period", "Day", "Hours", "Category", "Purpose", "Accomplished"]

    return DataFrame(resp, columns=columns)


def write_assets_to_gcs(
    csv_path: str,
    pdf_path: str,
    client_name: str,
    storage_client: storage.Client,
    bucket_name: str,
) -> None:
    """
    Persists the email assets to a GCS bucket for record-keeping.

    Args:
        csv_path (str): Path to the CSV attachment.
        pdf_path (str): Path to the PDF attachment.
        client_name (str): Name of the client for whom the assets are generated.
        storage_client (storage.Client): Initialized GCS storage client.
        bucket_name (str): GCS bucket name to upload email assets to.
    """

    bucket = storage_client.bucket(bucket_name)
    client_name = client_name.replace(" ", "_").lower().strip()
    today = datetime.now(pytz.timezone("America/New_York")).strftime("%Y-%m-%d")

    for filename in [os.path.basename(csv_path), os.path.basename(pdf_path)]:
        local_path = os.path.join(os.path.dirname(csv_path), filename)
        gcs_path = f"{client_name}/{today}/{filename}"

        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)

        application_logger.debug(f"*** Uploaded {local_path} to gs://{bucket_name}/{gcs_path}")


def get_data_for_environment(
    is_prod_run: bool,
    storage_client: storage.Client,
    bucket_name: str,
    blob_name: str = "contracting_config.json",
) -> Tuple[dict, dict]:
    """
    Returns the appropriate configuration dictionaries based on the environment.

    Args:
        is_prod_run (bool): Flag indicating if the run is for production.
        storage_client (storage.Client): Initialized GCS storage client.
        bucket_name (str): GCS bucket name to upload email assets to.
        blob_name (str): Name of the blob containing the configuration (default: contracting_config.json).

    Returns:
        Tuple[dict, dict]: A tuple containing the configuration dictionaries.
    """

    if is_prod_run:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        config_data = blob.download_as_text()

        config_json = json.loads(config_data)
        return config_json["clients"], config_json["globals"]

    # If we're running locally, we'll use the dev config
    # that isn't pushed to version control
    else:
        from config import CONSULTANT_MAP, GLOBAL_MAP

        return CONSULTANT_MAP, GLOBAL_MAP
