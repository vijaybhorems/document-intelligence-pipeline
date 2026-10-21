# Scheduled work (SPEC §9, §20): Cloud Scheduler → Cloud Run Jobs, same image as the
# services, different command.
#
#   dip-compactor  records/*.json -> lake/*.parquet, hourly        (sa-compactor)
#   dip-sweeper    re-send stranded jobs, every 10 minutes         (sa-sweeper)

resource "google_service_account" "compactor" {
  account_id   = "sa-compactor"
  display_name = "dip compactor (Cloud Run Job)"
}

resource "google_service_account" "sweeper" {
  account_id   = "sa-sweeper"
  display_name = "dip sweeper (Cloud Run Job)"
}

resource "google_service_account" "scheduler" {
  account_id   = "sa-scheduler"
  display_name = "Cloud Scheduler -> dip jobs"
}

# ---------------------------------------------------------------- compactor access

# Reads everything (records/ is its input); writes, overwrites and deletes only under
# lake/. The condition is evaluated per object, so a bug can't touch records/ or raw/.
resource "google_storage_bucket_iam_member" "compactor_reads" {
  bucket = google_storage_bucket.docs.name
  role   = "roles/storage.objectViewer"
  member = google_service_account.compactor.member
}

resource "google_storage_bucket_iam_member" "compactor_writes_lake" {
  bucket = google_storage_bucket.docs.name
  role   = "roles/storage.objectUser"
  member = google_service_account.compactor.member

  condition {
    title      = "lake-only"
    expression = "resource.name.startsWith(\"projects/_/buckets/${google_storage_bucket.docs.name}/objects/lake/\")"
  }
}

# ---------------------------------------------------------------- sweeper access

resource "google_project_iam_member" "sweeper_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = google_service_account.sweeper.member
}

resource "google_cloud_tasks_queue_iam_member" "sweeper_enqueues" {
  name     = google_cloud_tasks_queue.jobs.name
  location = var.region
  role     = "roles/cloudtasks.enqueuer"
  member   = google_service_account.sweeper.member
}

resource "google_service_account_iam_member" "sweeper_acts_as_invoker" {
  service_account_id = google_service_account.tasks_invoker.name
  role               = "roles/iam.serviceAccountUser"
  member             = google_service_account.sweeper.member
}

# ---------------------------------------------------------------- the jobs

locals {
  jobs = {
    compactor = {
      sa   = google_service_account.compactor.email
      args = ["compact"]
      env  = { DIP_ENV = var.env, DIP_BACKEND = "gcp", DIP_GCS_BUCKET = google_storage_bucket.docs.name }
    }
    sweeper = {
      sa   = google_service_account.sweeper.email
      args = ["sweep"]
      env  = local.common_env # needs the queue, worker URL and invoker to re-enqueue
    }
  }
}

resource "google_cloud_run_v2_job" "this" {
  for_each = local.jobs

  name                = "dip-${each.key}"
  location            = var.region
  deletion_protection = var.env == "prod"

  template {
    task_count = 1
    template {
      service_account = each.value.sa
      timeout         = "600s"
      max_retries     = 1

      containers {
        image   = var.image
        command = ["dip"]
        args    = each.value.args

        resources {
          limits = { cpu = "1", memory = "1Gi" }
        }

        dynamic "env" {
          for_each = merge(each.value.env, { DIP_LOG_LEVEL = "INFO" })
          content {
            name  = env.key
            value = env.value
          }
        }
      }
    }
  }

  lifecycle {
    ignore_changes = [template[0].template[0].containers[0].image, client, client_version]
  }

  depends_on = [google_project_service.this]
}

resource "google_cloud_run_v2_job_iam_member" "scheduler_runs" {
  for_each = google_cloud_run_v2_job.this

  name     = each.value.name
  location = var.region
  role     = "roles/run.invoker" # includes run.jobs.run
  member   = google_service_account.scheduler.member
}

resource "google_cloud_scheduler_job" "this" {
  for_each = {
    compactor = var.compact_schedule
    sweeper   = var.sweep_schedule
  }

  name             = "dip-${each.key}"
  region           = var.region
  schedule         = each.value
  time_zone        = "Etc/UTC"
  attempt_deadline = "60s" # starting the job, not running it

  http_target {
    http_method = "POST"
    uri         = "https://run.googleapis.com/v2/${google_cloud_run_v2_job.this[each.key].id}:run"

    oauth_token {
      service_account_email = google_service_account.scheduler.email
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }
  }

  depends_on = [google_cloud_run_v2_job_iam_member.scheduler_runs]
}
