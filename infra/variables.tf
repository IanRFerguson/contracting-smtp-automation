variable "project_id" {
  description = "Target project ID to write to"
  type        = string
}

variable "bucket_name" {
  description = "GCS bucket name to upload email assets to"
  type        = string
}

variable "resend_api_key" {
  description = "API key for Resend email service"
  type        = string
}

variable "image_name" {
  description = "Container image name for the Cloud Run job"
  type        = string
}

variable "alert_email" {
  description = "Email address to receive alerts"
  type        = string
}
