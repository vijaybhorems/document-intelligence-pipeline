# CI/CD without keys (SPEC §13): GitHub's OIDC token is exchanged for a short-lived
# Google token through Workload Identity Federation. Nothing to leak, nothing to rotate.
#
# Only pushes to main of this exact repository (by numeric ID) can deploy. The repo is
# public, so the condition is what stops a fork's workflow from asking for a token.

resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github"
  display_name              = "GitHub Actions"

  depends_on = [google_project_service.this]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-oidc"
  display_name                       = "GitHub OIDC"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  attribute_mapping = {
    "google.subject"          = "assertion.sub"
    "attribute.repository"    = "assertion.repository"
    "attribute.repository_id" = "assertion.repository_id"
    "attribute.ref"           = "assertion.ref"
    "attribute.workflow_ref"  = "assertion.job_workflow_ref"
  }

  attribute_condition = <<-CEL
    assertion.repository_id == "${var.github_repository_id}" &&
    assertion.repository == "${var.github_repository}" &&
    assertion.ref == "refs/heads/main"
  CEL
}

resource "google_service_account" "deployer" {
  account_id   = "sa-deployer"
  display_name = "GitHub Actions deployer"
}

resource "google_service_account_iam_member" "github_impersonates_deployer" {
  service_account_id = google_service_account.deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository_id/${var.github_repository_id}"
}

# What a deploy needs, and no more: push to this one repository, update these two
# services, and run their revisions as their own service accounts. No Terraform, no IAM.
resource "google_artifact_registry_repository_iam_member" "deployer_pushes" {
  repository = google_artifact_registry_repository.images.name
  location   = var.region
  role       = "roles/artifactregistry.writer"
  member     = google_service_account.deployer.member
}

resource "google_cloud_run_v2_service_iam_member" "deployer_updates" {
  for_each = {
    api    = google_cloud_run_v2_service.api.name
    worker = google_cloud_run_v2_service.worker.name
  }

  name     = each.value
  location = var.region
  role     = "roles/run.developer"
  member   = google_service_account.deployer.member
}

resource "google_service_account_iam_member" "deployer_acts_as" {
  for_each = {
    api    = google_service_account.api.name
    worker = google_service_account.worker.name
  }

  service_account_id = each.value
  role               = "roles/iam.serviceAccountUser"
  member             = google_service_account.deployer.member
}
