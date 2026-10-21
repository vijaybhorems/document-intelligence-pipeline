# ADR I10: Who changes what in the cloud

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-21 |
| **Spec ref** | SPEC §13, §18; decisions I6 (Terraform), I3 (one image, two services) |

## Context

SPEC §13 first sketched CI running `terraform apply` on every merge. That gives a GitHub workflow, which in a **public** repository is triggered by anyone's pull request once merged, an identity that can change everything: IAM, secrets, the database, the Workload Identity pool that trusts GitHub in the first place. If that identity leaks, or the workflow is compromised through a dependency, the attacker owns the project.

Most merges change application code, not infrastructure. Shipping them needs a tiny fraction of those permissions.

## Options considered

1. **CI applies Terraform on merge.** Fully automated. The CI identity needs owner-level roles (IAM admin, Secret Manager admin, Firestore admin...).
2. **A person applies Terraform; CI only ships images.** CI can push to one Artifact Registry repository and update two Cloud Run services. Terraform ignores the image field so the two never fight.
3. **CI runs `terraform plan` on PRs, a person applies.** Better review, but plan still needs read access to secrets metadata and IAM. That's a later improvement, not a different trust model.

## Decision

**Option 2.** `infra/terraform` is applied by a person with their own short-lived gcloud credentials. On merge to `main`, `.github/workflows/deploy.yml` exchanges GitHub's OIDC token (Workload Identity Federation, no JSON keys) for `sa-deployer`, which can only:

- push images to `…/dip` (`artifactregistry.writer` on that repository);
- update `dip-api` and `dip-worker` (`run.developer` on those two services);
- run revisions as `sa-api` and `sa-worker` (`serviceAccountUser` on those two accounts).

The Workload Identity provider accepts only tokens for this repository's numeric ID **and** name, from `refs/heads/main`.

## Consequences

- **A leaked deployer token can't escalate.** At worst it deploys a bad image to dev, which is visible in the revision history and reverted with one command (see the runbook).
- **Infrastructure drift is possible.** A merged Terraform change does nothing until someone applies it. The PR template and the phase notes call it out, and `terraform plan` showing changes is the signal.
- Terraform has `ignore_changes` on the container image, so a later `terraform apply` never rolls the services back to the first-deploy image.
- **When we'd revisit this:** with a team, or with prod changes needing an audit trail. Then use option 3 plus a separate, approval-gated `terraform apply` workflow running as a different, more privileged identity, bound to a protected GitHub environment.
