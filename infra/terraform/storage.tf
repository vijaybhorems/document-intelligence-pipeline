# Documents and records (SPEC §9.1), job state (ADR I4), container images.

resource "google_storage_bucket" "docs" {
  name     = "${var.project_id}-docs"
  location = var.region

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = var.env == "dev"

  # raw/ uploads are only needed until the record exists (and for re-extraction).
  # records/ is the source of truth and is kept.
  lifecycle_rule {
    condition {
      age            = var.raw_retention_days
      matches_prefix = ["raw/"]
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.this]
}

resource "google_firestore_database" "default" {
  name        = "(default)" # the free tier applies only to the default database
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  delete_protection_state = "DELETE_PROTECTION_ENABLED"
  deletion_policy         = "ABANDON" # `terraform destroy` never deletes job history

  depends_on = [google_project_service.this]
}

resource "google_artifact_registry_repository" "images" {
  repository_id = "dip"
  location      = var.region
  format        = "DOCKER"
  description   = "dip api/worker images, tagged by git SHA"

  cleanup_policy_dry_run = false
  cleanup_policies {
    id     = "keep-recent"
    action = "KEEP"
    most_recent_versions {
      keep_count = 10
    }
  }
  cleanup_policies {
    id     = "delete-old"
    action = "DELETE"
    condition {
      older_than = "2592000s" # 30 days; the 10 most recent are kept regardless
    }
  }

  depends_on = [google_project_service.this]
}

locals {
  image_repo = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.images.repository_id}/dip"
}
