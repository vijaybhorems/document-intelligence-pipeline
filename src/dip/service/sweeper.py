"""Re-send jobs that nothing will ever finish (SPEC §20, open question 9).

A job can be stranded: every delivery failed before reaching the app (worker down,
IAM not yet propagated, a deploy), or a worker died mid-job. Cloud Tasks then gives
up and nobody touches the job again. The sweeper runs on a schedule (Cloud Scheduler
→ Cloud Run Job), finds unfinished jobs with no update for ``STALE_AFTER``, and
enqueues them again, at most ``MAX_SWEEPS`` times before marking them failed.

``STALE_AFTER`` must exceed Cloud Tasks' retry window (``max_retry_duration``, 30 min
in infra/terraform/queue.tf). Otherwise the sweeper would re-send a job the queue is
still retrying, and two workers could extract the same contract and both be billed.
A running job can't look stale by mistake: the worker updates it at every stage, and
its request is killed at 15 minutes.
"""

import datetime as dt
from collections.abc import Callable
from dataclasses import dataclass, field

import structlog

from dip.service.jobs import JobStatus, JobStore, now
from dip.service.queue import TaskQueue

log = structlog.get_logger()

STALE_AFTER = dt.timedelta(minutes=35)
MAX_SWEEPS = 2


@dataclass
class SweepReport:
    requeued: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)


def sweep(
    jobs: JobStore,
    queue: TaskQueue,
    stale_after: dt.timedelta = STALE_AFTER,
    max_sweeps: int = MAX_SWEEPS,
    clock: Callable[[], dt.datetime] = now,
) -> SweepReport:
    report = SweepReport()
    for job in jobs.find_stale(clock() - stale_after):
        idle_min = round((clock() - job.updated_at).total_seconds() / 60)
        if job.sweeps >= max_sweeps:
            error = f"stale: unfinished after {job.sweeps} re-sends (last stage {job.status.value})"
            jobs.update(job.job_id, status=JobStatus.FAILED, error=error)
            log.error("sweeper.gave_up", job_id=job.job_id, sweeps=job.sweeps, idle_min=idle_min)
            report.failed.append(job.job_id)
            continue
        jobs.update(job.job_id, status=JobStatus.QUEUED, sweeps=job.sweeps + 1)
        queue.enqueue(job.job_id)
        log.warning(
            "sweeper.requeued",
            job_id=job.job_id,
            stage=job.status.value,
            sweep=job.sweeps + 1,
            idle_min=idle_min,
        )
        report.requeued.append(job.job_id)
    return report
