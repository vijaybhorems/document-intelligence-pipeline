output "api_url" {
  value = google_cloud_run_v2_service.api.uri
}

output "worker_url" {
  value = local.worker_url
}

output "image_repo" {
  description = "Push images here: <image_repo>:<git sha>."
  value       = local.image_repo
}

output "docs_bucket" {
  value = google_storage_bucket.docs.name
}

# The GitHub Actions variables the deploy workflow reads (`gh variable set`).
output "github_actions_variables" {
  value = {
    GCP_PROJECT      = var.project_id
    GCP_REGION       = var.region
    GCP_WIF_PROVIDER = google_iam_workload_identity_pool_provider.github.name
    GCP_DEPLOYER_SA  = google_service_account.deployer.email
    GCP_IMAGE_REPO   = local.image_repo
  }
}
