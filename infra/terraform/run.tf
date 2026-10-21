# Cloud Run (SPEC §5, §13): one image, two services (ADR I3). DIP_ROLE picks the app.
#
#   dip-api     public; X-API-Key checked by the app; scales on requests
#   dip-worker  internal ingress; only sa-tasks-invoker may invoke (Cloud Run IAM), and
#               the app verifies the same OIDC token again (dip.service.auth)

locals {
  # Deterministic URL: known before the service exists, so the API can name the worker
  # and the worker can check that tokens were minted for it (the OIDC audience).
  worker_url = "https://dip-worker-${data.google_project.this.number}.${var.region}.run.app"
  queue_path = "projects/${var.project_id}/locations/${var.region}/queues/${google_cloud_tasks_queue.jobs.name}"

  common_env = {
    DIP_ENV                 = var.env
    DIP_LOG_LEVEL           = "INFO"
    DIP_BACKEND             = "gcp"
    DIP_GCS_BUCKET          = google_storage_bucket.docs.name
    DIP_TASKS_QUEUE         = local.queue_path
    DIP_WORKER_URL          = local.worker_url
    DIP_TASKS_INVOKER_EMAIL = google_service_account.tasks_invoker.email
  }
}

resource "google_cloud_run_v2_service" "api" {
  name     = "dip-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  # Public endpoint: no Cloud Run IAM check (and no allUsers binding); the app requires
  # an API key on every /v1 route.
  invoker_iam_disabled = true
  deletion_protection  = var.env == "prod"

  template {
    service_account                  = google_service_account.api.email
    timeout                          = "120s" # ?wait=true waits up to 60 s
    max_instance_request_concurrency = 40

    scaling {
      min_instance_count = 0
      max_instance_count = var.api_max_instances
    }

    containers {
      image = var.image

      resources {
        limits            = { cpu = "1", memory = "512Mi" }
        cpu_idle          = true # billed only while handling requests
        startup_cpu_boost = true
      }

      dynamic "env" {
        for_each = merge(local.common_env, { DIP_ROLE = "api" })
        content {
          name  = env.key
          value = env.value
        }
      }
      env {
        name = "DIP_API_KEYS"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.this["api-keys"].secret_id
            version = "latest"
          }
        }
      }

      startup_probe {
        http_get {
          path = "/health"
        }
        period_seconds    = 2
        failure_threshold = 15
      }
    }
  }

  lifecycle {
    # CI rolls out new images with `gcloud run deploy`; Terraform owns everything else.
    ignore_changes = [template[0].containers[0].image, client, client_version]
  }

  depends_on = [google_secret_manager_secret_iam_member.access]
}

resource "google_cloud_run_v2_service" "worker" {
  name     = "dip-worker"
  location = var.region

  # Reachable only from inside the project (Cloud Tasks counts, on the run.app URL).
  ingress             = "INGRESS_TRAFFIC_INTERNAL_ONLY"
  deletion_protection = var.env == "prod"

  template {
    service_account = google_service_account.worker.email
    # One request = one whole job. Matches CloudTasksQueue's dispatch deadline.
    timeout                          = "900s"
    max_instance_request_concurrency = var.worker_concurrency

    scaling {
      min_instance_count = 0
      max_instance_count = var.worker_max_instances
    }

    containers {
      image = var.image

      resources {
        limits            = { cpu = "1", memory = "2Gi" } # 25 MB PDFs, 300 pages, pdfium
        cpu_idle          = true
        startup_cpu_boost = true
      }

      dynamic "env" {
        for_each = merge(local.common_env, {
          DIP_ROLE          = "worker"
          DIP_OTEL_ENDPOINT = "https://otlp.arize.com/v1/traces"
          DIP_TRACE_CONTENT = tostring(var.trace_content)
        })
        content {
          name  = env.key
          value = env.value
        }
      }
      dynamic "env" {
        for_each = {
          DIP_OPENAI_API_KEY = "openai-api-key"
          DIP_OTEL_HEADERS   = "arize-otlp-headers"
        }
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.this[env.value].secret_id
              version = "latest"
            }
          }
        }
      }

      startup_probe {
        http_get {
          path = "/health"
        }
        period_seconds    = 2
        failure_threshold = 15
      }
    }
  }

  lifecycle {
    ignore_changes = [template[0].containers[0].image, client, client_version]
  }

  depends_on = [google_secret_manager_secret_iam_member.access]
}
