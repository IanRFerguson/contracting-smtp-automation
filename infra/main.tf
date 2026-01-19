/* 
    NOTE: We're opting to use a local backend here for simplicity, but 
    in a real-world scenario, consider using a remote backend like 
    Terraform Cloud, AWS S3, or GCS for better state management and collaboration. 
*/
locals {
  sa_permissions = [
    "bigquery.dataViewer",
    "bigquery.jobUser",
    "storage.admin"
  ]
}

terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.9.0"
    }
  }
}

provider "google" {
  project = var.project_id
}

// We'll use this service account to write to the bucket, read from BigQuery,
// and run the Cloud Run jobs
resource "google_service_account" "automation_sa" {
  account_id   = "contracting-automation-sa"
  display_name = "Service Account for Contracting SMTP Automation"
}

resource "google_project_iam_member" "automation_sa_bigquery_access" {
  for_each = toset(local.sa_permissions)
  project  = var.project_id
  role     = "roles/${each.value}"
  member   = "serviceAccount:${google_service_account.automation_sa.email}"
}

// This storage bucket will hold email assets like CSVs and PDFs
resource "google_storage_bucket" "email_assets_bucket" {
  name                     = var.bucket_name
  location                 = "US"
  public_access_prevention = "enforced"
}
