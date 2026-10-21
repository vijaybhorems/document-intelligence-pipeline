# Alerts (SPEC §11): structured log events -> log-based metrics -> email.
#
#   job.failed        a job used its last attempt (dip.service.processing)
#   sweeper.gave_up   a stranded job failed after its re-sends (dip.service.sweeper)
#   sweeper.requeued  a stranded job was re-sent: something upstream is dropping work

locals {
  log_events = {
    job_failed       = "job.failed"
    sweeper_gave_up  = "sweeper.gave_up"
    sweeper_requeued = "sweeper.requeued"
  }
}

resource "google_logging_metric" "events" {
  for_each = local.log_events

  name        = "dip/${each.key}"
  description = "Count of '${each.value}' log events"
  filter      = "jsonPayload.message=\"${each.value}\""

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }

  depends_on = [google_project_service.this]
}

resource "google_monitoring_notification_channel" "email" {
  for_each = toset(var.alert_emails)

  display_name = "dip alerts: ${each.value}"
  type         = "email"
  labels       = { email_address = each.value }
}

resource "google_monitoring_alert_policy" "events" {
  # resource: where the event is logged (Monitoring requires it in the filter).
  for_each = {
    job_failed       = { title = "A dip job failed permanently", severity = "ERROR", resource = "cloud_run_revision" }
    sweeper_gave_up  = { title = "A stranded dip job was abandoned", severity = "ERROR", resource = "cloud_run_job" }
    sweeper_requeued = { title = "dip jobs were stranded and re-sent", severity = "WARNING", resource = "cloud_run_job" }
  }

  display_name = each.value.title
  combiner     = "OR"
  severity     = each.value.severity

  conditions {
    display_name = "${local.log_events[each.key]} > 0 in 5 min"
    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/${google_logging_metric.events[each.key].name}\" AND resource.type=\"${each.value.resource}\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "0s"

      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_SUM"
        cross_series_reducer = "REDUCE_SUM"
      }
      trigger {
        count = 1
      }
    }
  }

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    mime_type = "text/markdown"
    content   = "See docs/runbook.md, \"A job failed or is stuck\". Logs: `jsonPayload.message=\"${local.log_events[each.key]}\"`."
  }

  notification_channels = [for c in google_monitoring_notification_channel.email : c.id]
}
