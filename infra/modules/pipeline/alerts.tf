# Log-based metric for Cloud Scheduler failures
resource "google_logging_metric" "scheduler_failure" {
  count = var.cron_schedule != "" ? 1 : 0

  name   = "${var.job_name}-scheduler-failure"
  filter = <<-EOT
    resource.type="cloud_scheduler_job"
    resource.labels.job_id="${var.job_name}-scheduler"
    resource.labels.location="${var.location}"
    (severity="ERROR" OR (protoPayload.status.code!=0 AND protoPayload.status.code!=NULL))
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
}

# Log-based metric for Cloud Run job failures
resource "google_logging_metric" "job_failure" {
  name   = "${var.job_name}-failure"
  filter = <<-EOT
    resource.type="cloud_run_job"
    resource.labels.job_name="${var.job_name}"
    resource.labels.location="${var.location}"
    (severity="ERROR" OR (jsonPayload.message=~".*failed.*" OR jsonPayload.message=~".*error.*"))
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
}

# Log-based metric for Cloud Run job success
resource "google_logging_metric" "job_success" {
  name   = "${var.job_name}-success"
  filter = <<-EOT
    resource.type="cloud_run_job"
    resource.labels.job_name="${var.job_name}"
    resource.labels.location="${var.location}"
    jsonPayload.message=~".*success.*|.*completed.*|.*finished.*"
    severity!="ERROR"
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
}

# Notification channel for email alerts
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Alert Channel"
  type         = "email"

  labels = {
    email_address = var.alert_email
  }
}

# Alert policy for Cloud Scheduler failures
resource "google_monitoring_alert_policy" "scheduler_failure_alert" {
  count = var.cron_schedule != "" ? 1 : 0

  display_name = "${var.job_name} - Scheduler Failure"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Scheduler failed to kick off job"

    condition_threshold {
      filter          = "resource.type=\"cloud_scheduler_job\" AND metric.type=\"logging.googleapis.com/user/${google_logging_metric.scheduler_failure[0].name}\""
      duration        = "0s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s" # 30 minutes
  }

  documentation {
    content   = "The Cloud Scheduler job ${var.job_name}-scheduler failed to trigger the Cloud Run job."
    mime_type = "text/markdown"
  }
}

# Alert policy for Cloud Run job failures
resource "google_monitoring_alert_policy" "job_failure_alert" {
  display_name = "${var.job_name} - Job Failure"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Run job execution failed"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_job\" AND metric.type=\"logging.googleapis.com/user/${google_logging_metric.job_failure.name}\""
      duration        = "0s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s" # 30 minutes
  }

  documentation {
    content   = "The Cloud Run job ${var.job_name} encountered an error during execution."
    mime_type = "text/markdown"
  }
}

# Alert policy for Cloud Run job success
resource "google_monitoring_alert_policy" "job_success_alert" {
  display_name = "${var.job_name} - Job Success"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Run job completed successfully"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_job\" AND metric.type=\"logging.googleapis.com/user/${google_logging_metric.job_success.name}\""
      duration        = "0s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "300s" # 5 minutes
  }

  documentation {
    content   = "The Cloud Run job ${var.job_name} completed successfully."
    mime_type = "text/markdown"
  }
}
