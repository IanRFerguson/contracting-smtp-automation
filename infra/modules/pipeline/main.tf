resource "google_cloud_run_v2_job" "email_job" {
  name     = var.job_name
  location = var.location

  template {
    template {
      max_retries     = 1
      service_account = var.service_account_email

      containers {
        image = var.image_name

        // Environment variables for the job
        env {
          name  = "GCS_BUCKET_NAME"
          value = var.gcs_bucket_name
        }

        env {
          name  = "RESEND_API_KEY"
          value = var.resend_api_key
        }

        env {
          name  = "STAGE"
          value = var.stage
        }
      }
    }
  }
}

# Cloud Scheduler job (only created if schedule is provided)
resource "google_cloud_scheduler_job" "scheduled_job" {
  count = var.cron_schedule != "" ? 1 : 0

  name             = "${lower(var.job_name)}-scheduler"
  description      = "Scheduled trigger for ${var.job_name}"
  schedule         = var.cron_schedule
  time_zone        = var.time_zone
  region           = var.location
  attempt_deadline = "600s"

  retry_config {
    retry_count = 3
  }

  http_target {
    http_method = "POST"
    uri         = "https://${var.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.email_job.name}:run"

    oauth_token {
      service_account_email = var.service_account_email
    }
  }
}

