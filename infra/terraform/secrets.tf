# Secret *containers* only. Values are added out of band (infra/bootstrap/dip-secrets.sh,
# `gcloud secrets versions add`), so they never appear in Terraform state or plans.

locals {
  secrets = {
    "openai-api-key"     = "OpenAI key used by the worker."
    "api-keys"           = "Comma-separated X-API-Key values the public API accepts."
    "arize-otlp-headers" = "OTLP headers for Arize: space_id=...,api_key=..."
  }
}

resource "google_secret_manager_secret" "this" {
  for_each = local.secrets

  secret_id = each.key
  labels    = { purpose = replace(each.key, "-", "_") }
  annotations = {
    description = each.value
  }

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }

  depends_on = [google_project_service.this]
}
