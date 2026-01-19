variable "project_id" {
  description = "Target project ID to write to"
  type        = string
}

variable "bucket_name" {
  description = "GCS bucket name to upload email assets to"
  type        = string
}

variable "smtp_username" {
  description = "SMTP username for sending emails"
  type        = string
}

variable "smtp_password" {
  description = "SMTP password for seding emails"
  type        = string
  sensitive   = true
}
