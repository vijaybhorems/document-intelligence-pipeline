# dip-mcp (SPEC §12.2.2): the MCP server, Streamable HTTP (stateless), Google OAuth.
#
# Created only once an OAuth client exists (var.mcp_oauth_client_id; see
# infra/bootstrap/dip-mcp-oauth.sh). The server needs only the client *ID*: it checks
# that tokens were issued to it. The client secret belongs to MCP clients (Inspector),
# never to the server, so it isn't stored here.

locals {
  mcp_enabled = var.mcp_oauth_client_id != ""
  mcp_url     = "https://dip-mcp-${data.google_project.this.number}.${var.region}.run.app"
}

resource "google_service_account" "mcp" {
  account_id   = "sa-mcp"
  display_name = "dip MCP server (Cloud Run)"
}

# Least privilege (SPEC §12.2.5): enqueue, read records and lake, write uploads, read
# and write jobs, principals and usage. No secrets.
resource "google_storage_bucket_iam_member" "mcp_docs" {
  for_each = toset(["roles/storage.objectCreator", "roles/storage.objectViewer"])

  bucket = google_storage_bucket.docs.name
  role   = each.value
  member = google_service_account.mcp.member
}

resource "google_project_iam_member" "mcp_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = google_service_account.mcp.member
}

resource "google_cloud_tasks_queue_iam_member" "mcp_enqueues" {
  name     = google_cloud_tasks_queue.jobs.name
  location = var.region
  role     = "roles/cloudtasks.enqueuer"
  member   = google_service_account.mcp.member
}

resource "google_service_account_iam_member" "mcp_acts_as_invoker" {
  service_account_id = google_service_account.tasks_invoker.name
  role               = "roles/iam.serviceAccountUser"
  member             = google_service_account.mcp.member
}

resource "google_cloud_run_v2_service" "mcp" {
  count = local.mcp_enabled ? 1 : 0

  name     = "dip-mcp"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  # Google OAuth is checked by the app (dip.mcp_server.auth): Cloud Run IAM can't
  # validate Google *access* tokens issued to our OAuth client.
  invoker_iam_disabled = true
  deletion_protection  = var.env == "prod"

  template {
    service_account                  = google_service_account.mcp.email
    timeout                          = "60s" # submit_extraction waits at most 25 s
    max_instance_request_concurrency = 40

    scaling {
      min_instance_count = 0
      max_instance_count = var.mcp_max_instances
    }

    containers {
      image = var.image

      resources {
        limits            = { cpu = "1", memory = "1Gi" } # DuckDB for search_records
        cpu_idle          = true
        startup_cpu_boost = true
      }

      dynamic "env" {
        for_each = merge(local.common_env, {
          DIP_ROLE                = "mcp_server"
          DIP_MCP_OAUTH_CLIENT_ID = var.mcp_oauth_client_id
          DIP_MCP_PUBLIC_URL      = local.mcp_url
          # Browser origins allowed to call /mcp: MCP Inspector, under either loopback name.
          DIP_MCP_ALLOWED_ORIGINS = jsonencode(["http://localhost:6274", "http://127.0.0.1:6274"])
        })
        content {
          name  = env.key
          value = env.value
        }
      }

      startup_probe {
        http_get {
          path = "/health"
        }
        period_seconds    = 2
        failure_threshold = local.startup_probe_failures
      }
    }
  }

  lifecycle {
    ignore_changes = [template[0].containers[0].image, client, client_version]
  }

  depends_on = [google_project_iam_member.mcp_firestore]
}

resource "google_cloud_run_v2_service_iam_member" "deployer_updates_mcp" {
  count = local.mcp_enabled ? 1 : 0

  name     = google_cloud_run_v2_service.mcp[0].name
  location = var.region
  role     = "roles/run.developer"
  member   = google_service_account.deployer.member
}

resource "google_service_account_iam_member" "deployer_acts_as_mcp" {
  service_account_id = google_service_account.mcp.name
  role               = "roles/iam.serviceAccountUser"
  member             = google_service_account.deployer.member
}

output "mcp_url" {
  description = "Connect MCP clients to <mcp_url>/mcp."
  value       = local.mcp_enabled ? local.mcp_url : null
}
