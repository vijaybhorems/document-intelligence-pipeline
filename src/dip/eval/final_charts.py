"""Charts for the final report (SPEC §15.2): field types, per-field heatmap, phrasing slice.

Same visual system as ``dip.eval.charts`` (Phase 6): the validated categorical slots,
recessive grid, direct labels, so identity never relies on colour alone. Sequential
data (the heatmap) uses one hue, light to dark, with the value printed in each cell.
"""

from dataclasses import dataclass
from pathlib import Path

from dip.eval.bootstrap import bootstrap
from dip.eval.charts import GRID, SURFACE, TEXT_PRIMARY, TEXT_SECONDARY
from dip.eval.matchers import Counts
from dip.eval.runs import load_results
from dip.eval.scorer import aggregate, per_field, slice_recall
from dip.eval.slices import Slice
from dip.schema.registry import FIELDS

TYPES = ("clause", "date", "duration", "entity_list", "jurisdiction", "text", "all")
TYPE_LABELS = {
    "clause": "clauses (33)",
    "date": "dates (3)",
    "duration": "durations (2)",
    "entity_list": "parties",
    "jurisdiction": "governing law",
    "text": "document name",
    "all": "all 41 fields",
}
FIELD_TYPE = {f.name: f.field_type.value for f in FIELDS}
# Label placement on the precision/recall panel (points, alignment): the typed fields sit
# close together near the top right, so each gets its own side instead of colliding.
PR_LABEL = {
    "clause": ((8, -3), "left"),
    "date": ((-8, 4), "right"),
    "duration": ((8, -12), "left"),
    "entity_list": ((8, 2), "left"),
    "jurisdiction": ((8, 2), "left"),
    "text": ((-8, -12), "right"),
    "all": ((8, -3), "left"),
}


@dataclass(frozen=True)
class System:
    label: str
    run_dir: Path
    color: str
    marker: str


@dataclass(frozen=True)
class TypeScore:
    precision: float | None
    recall: float | None
    f1: float | None
    low: float
    high: float


def type_scores(run_dir: Path) -> dict[str, TypeScore]:
    """Headline micro P/R/F1 per field type and overall, with bootstrap 95% CIs."""
    results = load_results(run_dir)
    counts = per_field(results, None)
    out = {}
    for group_of, groups in ((FIELD_TYPE.get, TYPES[:-1]), (lambda _: "all", ("all",))):
        scores = aggregate(counts, group_of)
        cis = bootstrap(results, None, group_of)["micro"]
        for g in groups:
            micro = scores[g].micro
            out[g] = TypeScore(micro.precision, micro.recall, micro.f1, cis[g].low, cis[g].high)
    return out


def _axes_style(ax) -> None:
    ax.set_facecolor(SURFACE)
    ax.grid(True, axis="x", color=GRID, linewidth=0.8)
    ax.tick_params(colors=TEXT_SECONDARY, labelsize=8)
    for spine in ax.spines.values():
        spine.set_visible(False)


def render_field_types(systems: list[System], out: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    scores = {s.label: type_scores(s.run_dir) for s in systems}
    fig, (left, right) = plt.subplots(
        1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1.35, 1]}, facecolor=SURFACE
    )
    rows = list(reversed(TYPES))
    offsets = {s.label: (i - (len(systems) - 1) / 2) * 0.22 for i, s in enumerate(systems)}
    for s in systems:
        for y, t in enumerate(rows):
            sc = scores[s.label][t]
            if sc.f1 is None:
                continue
            yy = y + offsets[s.label]
            left.plot(
                [100 * sc.low, 100 * sc.high], [yy, yy], color=s.color, linewidth=2, alpha=0.5
            )
            left.scatter(100 * sc.f1, yy, s=60, color=s.color, marker=s.marker, zorder=3,
                         edgecolors=SURFACE, linewidths=1.5)  # fmt: skip
    left.set_yticks(
        range(len(rows)), [TYPE_LABELS[t] for t in rows], color=TEXT_PRIMARY, fontsize=9
    )
    left.set_xlim(0, 100)
    left.set_xlabel("headline micro F1, 95% CI", fontsize=9, color=TEXT_SECONDARY)
    left.set_title("F1 by field type", loc="left", fontsize=11, color=TEXT_PRIMARY)
    _axes_style(left)

    main = systems[0]
    for t in TYPES:
        sc = scores[main.label][t]
        if sc.precision is None or sc.recall is None:
            continue
        right.scatter(100 * sc.recall, 100 * sc.precision, s=60, color=main.color,
                      marker=main.marker, zorder=3, edgecolors=SURFACE, linewidths=1.5)  # fmt: skip
        offset, align = PR_LABEL[t]
        right.annotate(
            TYPE_LABELS[t],
            (100 * sc.recall, 100 * sc.precision),
            xytext=offset,
            textcoords="offset points",
            ha=align,
            fontsize=8,
            color=TEXT_PRIMARY,
        )
    right.plot([0, 100], [0, 100], color=GRID, linewidth=1, linestyle="--", zorder=1)
    points = [scores[main.label][t] for t in TYPES]
    lows = [100 * v for p in points for v in (p.precision, p.recall) if v is not None]
    floor = max(0, min(lows) - 8)
    right.set_xlim(floor, 102)
    right.set_ylim(floor, 102)
    right.set_xlabel("recall", fontsize=9, color=TEXT_SECONDARY)
    right.set_ylabel("precision", fontsize=9, color=TEXT_SECONDARY)
    right.set_title(
        f"Precision vs recall: {main.label}", loc="left", fontsize=11, color=TEXT_PRIMARY
    )
    _axes_style(right)
    right.grid(True, axis="y", color=GRID, linewidth=0.8)

    handles = [
        Line2D([], [], marker=s.marker, linestyle="", color=s.color, markersize=8, label=s.label)
        for s in systems
    ]
    fig.legend(handles=handles, loc="lower center", frameon=False, fontsize=9, ncols=len(handles))
    fig.suptitle(title, x=0.01, ha="left", fontsize=12, color=TEXT_PRIMARY)
    fig.tight_layout(rect=(0, 0.07, 1, 0.94))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160, facecolor=SURFACE)
    plt.close(fig)


def render_field_heatmap(run_dir: Path, out: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    counts = per_field(load_results(run_dir), None)
    rows = sorted(
        ((name, c) for name, c in counts.items()),
        key=lambda nc: (-(nc[1].f1 or 0), nc[0]),
    )
    data = [[c.precision, c.recall, c.f1] for _, c in rows]
    fig, ax = plt.subplots(figsize=(6.4, 0.24 * len(rows) + 1.4), facecolor=SURFACE)
    grid = [[(v if v is not None else float("nan")) for v in row] for row in data]
    ax.imshow(grid, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    for y, row in enumerate(data):
        for x, v in enumerate(row):
            text = chr(0x2013) if v is None else f"{100 * v:.0f}"
            dark = v is not None and v > 0.6
            ax.text(x, y, text, ha="center", va="center", fontsize=7,
                    color="white" if dark else TEXT_PRIMARY)  # fmt: skip
    labels = [f"{name}  (n={c.tp + c.fn})" for name, c in rows]
    ax.set_yticks(range(len(rows)), labels, fontsize=7, color=TEXT_PRIMARY)
    ax.set_xticks(range(3), ["precision", "recall", "F1"], fontsize=8, color=TEXT_PRIMARY)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(title, loc="left", fontsize=10, color=TEXT_PRIMARY, pad=24)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160, facecolor=SURFACE)
    plt.close(fig)


def phrasing_recall(run_dir: Path) -> dict[Slice, float | None]:
    """Clause recall pooled over fields, split by how gold phrases the clause."""
    pooled: dict[Slice, Counts] = {Slice.CANONICAL: Counts(), Slice.NON_CANONICAL: Counts()}
    for field, by_slice in slice_recall(load_results(run_dir)).items():
        if FIELD_TYPE.get(field) != "clause":
            continue
        for sl, c in by_slice.items():
            pooled[sl] = pooled[sl] + c
    return {sl: c.recall for sl, c in pooled.items()}


def render_phrasing(systems: list[System], out: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.5, 0.45 * len(systems) + 1.3), facecolor=SURFACE)
    for y, s in enumerate(reversed(systems)):
        r = phrasing_recall(s.run_dir)
        canon, non = r[Slice.CANONICAL], r[Slice.NON_CANONICAL]
        if canon is None or non is None:
            continue
        ax.plot([100 * non, 100 * canon], [y, y], color=GRID, linewidth=3, zorder=1)
        ax.scatter(100 * non, y, s=70, marker="o", facecolors=SURFACE, edgecolors=s.color,
                   linewidths=2, zorder=3)  # fmt: skip
        ax.scatter(100 * canon, y, s=70, marker="o", color=s.color, zorder=3)
        ax.annotate(f"gap {100 * (canon - non):.1f}", (100 * canon, y), xytext=(8, -3),
                    textcoords="offset points", fontsize=8, color=TEXT_PRIMARY)  # fmt: skip
    ax.set_yticks(range(len(systems)), [s.label for s in reversed(systems)], fontsize=9,
                  color=TEXT_PRIMARY)  # fmt: skip
    ax.set_xlim(40, 105)
    ax.set_ylim(-0.6, len(systems) - 0.4)
    ax.set_xlabel("clause recall: ○ unusual wording (non-canonical)  ● usual wording",
                  fontsize=9, color=TEXT_SECONDARY)  # fmt: skip
    ax.set_title(title, loc="left", fontsize=11, color=TEXT_PRIMARY)
    _axes_style(ax)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160, facecolor=SURFACE)
    plt.close(fig)
