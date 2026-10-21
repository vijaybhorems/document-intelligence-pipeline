variable "project_id" {
  type        = string
  description = "GCP project for this environment (created by infra/bootstrap/gcp-bootstrap.sh)."
}

variable "env" {
  type        = string
  description = "dev or prod. Sets DIP_ENV, labels and protections."

  validation {
    condition     = contains(["dev", "prod"], var.env)
    error_message = "env must be dev or prod."
  }
}

variable "region" {
  type        = string
  description = "One region for everything. Firestore's location can never change."
  default     = "us-central1"
}

variable "github_repository" {
  type        = string
  description = "owner/name of the repository whose main branch may deploy."
}

variable "github_repository_id" {
  type        = string
  description = "Numeric repository ID. Pinned as well as the name: a deleted and re-created repo with the same name gets a new ID, so it can't inherit deploy rights."
}

variable "image" {
  type        = string
  description = "Image for the first deploy only. Afterwards CI rolls out new digests and Terraform ignores the field."
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "trace_content" {
  type        = bool
  description = "Send prompt and response text to Arize. CUAD filings are public; real documents are not."
  default     = true
}

variable "worker_max_instances" {
  type        = number
  description = "Cost ceiling: at most this many workers (each runs up to worker_concurrency jobs)."
  default     = 2
}

variable "worker_concurrency" {
  type    = number
  default = 4
}

variable "api_max_instances" {
  type    = number
  default = 2
}

variable "tasks_max_concurrent" {
  type        = number
  description = "Jobs in flight across all workers. Keeps OpenAI requests under the account's rate limit."
  default     = 4
}

variable "tasks_max_per_second" {
  type    = number
  default = 1
}

variable "alert_emails" {
  type        = list(string)
  description = "Who gets alert emails. Set in a gitignored *.auto.tfvars, not in the public repo."
  default     = []
}

variable "compact_schedule" {
  type        = string
  description = "Cron for dip-compactor (UTC). Hourly: analytics lag records by at most an hour."
  default     = "5 * * * *"
}

variable "sweep_schedule" {
  type    = string
  default = "*/10 * * * *"
}

variable "raw_retention_days" {
  type        = number
  description = "Delete uploaded documents after this many days. Records are kept."
  default     = 30
}
