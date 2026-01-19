variable "job_name" {
  description = "Name of the Cloud Run job"
  type        = string
}

variable "cron_schedule" {
  description = "Cron schedule for the Cloud Scheduler job"
  type        = string
}

variable "gcs_bucket_name" {
  description = "GCS bucket name to upload email assets to"
  type        = string
}

variable "location" {
  description = "GCP location for deploying resources"
  type        = string
  default     = "us-central1"
}

variable "stage" {
  description = "Deployment stage (e.g., dev, prod)"
  type        = string
  default     = "production"
}

variable "smtp_username" {
  description = "SMTP username for sending emails"
  type        = string
}

variable "smtp_password" {
  description = "SMTP password for sending emails"
  type        = string
  sensitive   = true
}

variable "image_name" {
  description = "Container image name for the Cloud Run job"
  type        = string
}

variable "service_account_email" {
  description = "Service account email to run the Cloud Run job"
  type        = string
}

variable "time_zone" {
  description = "Time zone for the schedule (e.g., 'America/New_York')"
  type        = string
  default     = "UTC"
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "alert_email" {
  description = "Email address to receive alerts"
  type        = string
}
