# One root module for every environment; each has a tfvars file and a state prefix:
#
#   terraform init -backend-config=envs/dev.gcs.tfbackend
#   terraform plan -var-file=envs/dev.tfvars
#
# Applied by a person, not CI (ADR I10). CI only builds images and rolls them out.

terraform {
  required_version = ">= 1.9"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 8.6.0"
    }
  }

  backend "gcs" {} # bucket and prefix come from envs/<env>.gcs.tfbackend
}

provider "google" {
  project = var.project_id
  region  = var.region

  # Bill API calls to this project, not to whatever quota project the operator's
  # application-default credentials happen to carry.
  billing_project       = var.project_id
  user_project_override = true

  default_labels = {
    app = "dip"
    env = var.env
  }
}

data "google_project" "this" {}
