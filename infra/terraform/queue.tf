# Cloud Tasks (ADR I2): delivery, retries, and a rate cap that protects the OpenAI quota.

resource "google_cloud_tasks_queue" "jobs" {
  name     = "dip-jobs"
  location = var.region

  rate_limits {
    max_dispatches_per_second = var.tasks_max_per_second
    max_concurrent_dispatches = var.tasks_max_concurrent
  }

  # The worker allows a job 3 attempts (dip.service.processing.MAX_ATTEMPTS) and answers
  # 200 once it gives up, so the queue must allow at least that many deliveries. The
  # extra headroom covers deliveries that never reached the app (cold start, deploy).
  retry_config {
    max_attempts       = 5
    min_backoff        = "10s"
    max_backoff        = "300s"
    max_doublings      = 4
    max_retry_duration = "3600s"
  }

  stackdriver_logging_config {
    sampling_ratio = 1.0 # every delivery attempt is logged: cheap at this volume
  }

  depends_on = [google_project_service.this]
}
