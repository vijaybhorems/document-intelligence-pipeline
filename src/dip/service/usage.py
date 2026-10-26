"""Per-principal rate limits and daily spend caps (SPEC §12.2.7), checked before enqueueing.

Spend is reserved at submission from an estimate (pages x ``RESERVE_USD_PER_PAGE``)
and settled by the worker when the job finishes: plus the difference on success, or
minus the reserve on failure. So a burst of submissions can't overshoot the cap while
its jobs are still queued, and the total converges to what was actually spent.
"""

import datetime as dt
import threading
from typing import Protocol

# ~2x the scanned-route cost per page (Phase 9 load test: $0.0088 / 9 pages): a cap
# should err towards refusing, not overspending.
RESERVE_USD_PER_PAGE = 0.002


class LimitExceededError(Exception):
    def __init__(self, message: str, retry_after_s: int) -> None:
        super().__init__(message)
        self.retry_after_s = retry_after_s


class UsageStore(Protocol):
    def admit(self, principal: str, at: dt.datetime) -> tuple[int, float]:
        """Count one submission in this minute. Returns (submissions this minute, spent today)."""
        ...

    def add_spend(self, principal: str, day: dt.date, usd: float) -> None: ...


def _day(at: dt.datetime) -> str:
    return at.astimezone(dt.UTC).date().isoformat()


def _minute(at: dt.datetime) -> str:
    return at.astimezone(dt.UTC).strftime("%H:%M")


class MemoryUsageStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._spent: dict[tuple[str, str], float] = {}
        self._minutes: dict[tuple[str, str, str], int] = {}

    def admit(self, principal: str, at: dt.datetime) -> tuple[int, float]:
        with self._lock:
            key = (principal, _day(at), _minute(at))
            self._minutes[key] = self._minutes.get(key, 0) + 1
            return self._minutes[key], self._spent.get((principal, _day(at)), 0.0)

    def add_spend(self, principal: str, day: dt.date, usd: float) -> None:
        with self._lock:
            key = (principal, day.isoformat())
            self._spent[key] = self._spent.get(key, 0.0) + usd


class FirestoreUsageStore:
    """One document per principal per UTC day: ``{spent_usd, minute, minute_count}``."""

    def __init__(self, collection: str = "usage") -> None:
        from google.cloud import firestore

        self._client = firestore.Client()
        self._collection = self._client.collection(collection)

    def admit(self, principal: str, at: dt.datetime) -> tuple[int, float]:
        from google.cloud import firestore

        ref = self._collection.document(f"{principal}:{_day(at)}")
        minute = _minute(at)

        @firestore.transactional
        def bump(tx: firestore.Transaction) -> tuple[int, float]:
            snap = ref.get(transaction=tx)
            data = (snap.to_dict() or {}) if snap.exists else {}
            count = data.get("minute_count", 0) + 1 if data.get("minute") == minute else 1
            tx.set(ref, {"minute": minute, "minute_count": count}, merge=True)
            return count, float(data.get("spent_usd", 0.0))

        return bump(self._client.transaction())

    def add_spend(self, principal: str, day: dt.date, usd: float) -> None:
        from google.cloud import firestore

        ref = self._collection.document(f"{principal}:{day.isoformat()}")
        ref.set({"spent_usd": firestore.Increment(usd)}, merge=True)


def admit(
    store: UsageStore,
    principal: str,
    at: dt.datetime,
    *,
    per_minute: int,
    daily_cap_usd: float,
    reserve_usd: float,
) -> None:
    """Raise LimitExceededError, or record the submission and reserve its spend."""
    count, spent = store.admit(principal, at)
    if count > per_minute:
        raise LimitExceededError(
            f"rate limit: {per_minute} submissions per minute; wait and retry", retry_after_s=60
        )
    if spent + reserve_usd > daily_cap_usd:
        tomorrow = dt.datetime.combine(at.date() + dt.timedelta(days=1), dt.time(), dt.UTC)
        raise LimitExceededError(
            f"daily spend cap reached (${spent:.2f} of ${daily_cap_usd:.2f}); resets at 00:00 UTC",
            retry_after_s=int((tomorrow - at).total_seconds()),
        )
    store.add_spend(principal, at.astimezone(dt.UTC).date(), reserve_usd)
