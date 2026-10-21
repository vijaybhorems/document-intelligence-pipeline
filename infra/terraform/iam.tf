# One service account per job to do, each with only what that job needs (SPEC §18).
#
#   sa-api            writes uploads, reads records, creates jobs, enqueues tasks
#   sa-worker         reads uploads, writes records, updates jobs, calls OpenAI
#   sa-tasks-invoker  the identity Cloud Tasks signs its OIDC token as; may invoke the worker
#   sa-deployer       CI: pushes images, rolls out new revisions (github.tf)

resource "google_service_account" "api" {
  account_id   = "sa-api"
  display_name = "dip API (Cloud Run)"
}

resource "google_service_account" "worker" {
  account_id   = "sa-worker"
  display_name = "dip worker (Cloud Run)"
}

resource "google_service_account" "tasks_invoker" {
  account_id   = "sa-tasks-invoker"
  display_name = "Cloud Tasks -> dip worker (OIDC)"
}

# ---------------------------------------------------------------- data access

# Create + read, never delete or overwrite: uploads are content-addressed, records immutable.
resource "google_storage_bucket_iam_member" "docs" {
  for_each = {
    "api-create"    = { role = "roles/storage.objectCreator", member = google_service_account.api.member }
    "api-read"      = { role = "roles/storage.objectViewer", member = google_service_account.api.member }
    "worker-create" = { role = "roles/storage.objectCreator", member = google_service_account.worker.member }
    "worker-read"   = { role = "roles/storage.objectViewer", member = google_service_account.worker.member }
  }

  bucket = google_storage_bucket.docs.name
  role   = each.value.role
  member = each.value.member
}

# Firestore has no per-collection IAM; datastore.user is the narrowest predefined role.
resource "google_project_iam_member" "firestore" {
  for_each = {
    api    = google_service_account.api.member
    worker = google_service_account.worker.member
  }

  project = var.project_id
  role    = "roles/datastore.user"
  member  = each.value
}

resource "google_secret_manager_secret_iam_member" "access" {
  for_each = {
    "api-keys"           = google_service_account.api.member
    "openai-api-key"     = google_service_account.worker.member
    "arize-otlp-headers" = google_service_account.worker.member
  }

  secret_id = google_secret_manager_secret.this[each.key].id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value
}

# ---------------------------------------------------------------- the job path

resource "google_cloud_tasks_queue_iam_member" "api_enqueues" {
  name     = google_cloud_tasks_queue.jobs.name
  location = var.region
  role     = "roles/cloudtasks.enqueuer"
  member   = google_service_account.api.member
}

# Creating a task that carries an OIDC token *as* sa-tasks-invoker requires actAs on it.
# Without this, anyone who could enqueue could mint worker-invoking tokens.
resource "google_service_account_iam_member" "api_acts_as_invoker" {
  service_account_id = google_service_account.tasks_invoker.name
  role               = "roles/iam.serviceAccountUser"
  member             = google_service_account.api.member
}

resource "google_cloud_run_v2_service_iam_member" "invoker_calls_worker" {
  name     = google_cloud_run_v2_service.worker.name
  location = var.region
  role     = "roles/run.invoker"
  member   = google_service_account.tasks_invoker.member
}
