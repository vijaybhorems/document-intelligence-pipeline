"""Cost vs quality (Pareto) charts for decisions D1/D2 (SPEC §6.4).

One panel per input variant (clean, scanned), same y scale. x = total cost per
contract (API + parsing compute), log scale; y = overall headline micro F1 with
a 95% bootstrap CI. Color = model (3 validated slots: the scatter cap for
all-pairs distinguishability); marker + direct label = route, so identity is
never color-alone. The muted step line is the Pareto frontier: points that no
other point beats on both cost and F1.

Palette: dataviz reference instance, slots 1-3, validated all-pairs on the light
surface (aqua < 3:1 contrast, relieved by direct labels and the ADR table).
"""

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from dip.eval.bootstrap import bootstrap
from dip.eval.runs import load_meta, load_results
from dip.eval.scorer import aggregate, per_field

SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e8e7e3"
FRONTIER = "#a8a7a2"
MODEL_COLORS = {"gpt-5.6-luna": "#2a78d6", "gpt-5.6-terra": "#eb6834", "gpt-5.6-sol": "#1baf7a"}
ROUTE_MARKERS = {"txt": "o", "pypdf": "s", "docling": "D", "multimodal": "^", "hybrid": "P"}
# Label placement per route (points, alignment): routes sit close together in cost and
# F1, so each gets its own side instead of an automatic offset that collides.
LABEL_OFFSETS = {
    "txt": ((-9, 6), "right"),
    "pypdf": ((9, 6), "left"),
    "docling": ((9, -14), "left"),
    "multimodal": ((9, -14), "left"),
    "hybrid": ((9, 6), "left"),
}
COST_TICKS = (0.0025, 0.005, 0.01, 0.02, 0.05, 0.1)
OFF_SCALE_F1 = 0.2  # below this a route has collapsed: pin it to the edge, label it
ROUTE_LABELS = {
    "txt": "CUAD txt",
    "pypdf": "pypdf",
    "docling": "Docling",
    "multimodal": "multimodal",
}


@dataclass(frozen=True)
class Point:
    model: str
    route: str
    variant: str
    cost: float  # USD per contract, API + compute
    f1: float
    low: float
    high: float
    runs: int


def _key(config: dict[str, object]) -> tuple[str, str, str] | None:
    """Only comparable runs: prompt v4, full context, no derived validation."""
    if config.get("prompt_version", "v1") != "v4" or config.get("context", "full") != "full":
        return None
    return (
        str(config["model"]),
        str(config.get("route", "txt")),
        str(config.get("variant", "clean")),
    )


def collect_points(runs_dir: Path, split: str) -> list[Point]:
    groups: dict[tuple[str, str, str], list[Path]] = defaultdict(list)
    for run_dir in sorted(runs_dir.glob(f"*-{split}")):
        if not (run_dir / "field_results.parquet").exists():
            continue
        meta = load_meta(run_dir)
        if meta.derived_from or not meta.complete or "model" not in meta.config:
            continue
        if (key := _key(meta.config)) is not None:
            groups[key].append(run_dir)
    points = []
    for (model, route, variant), dirs in sorted(groups.items()):
        f1s, costs = [], []
        for d in dirs:
            meta = load_meta(d)
            results = load_results(d)
            f1s.append(aggregate(per_field(results, None), lambda f: "all")["all"].micro_f1 or 0.0)
            costs.append((meta.usage.cost_usd + meta.usage.compute_usd) / meta.n_docs)
        ci = bootstrap(load_results(dirs[0]), None, lambda f: "all")["micro"]["all"]
        mean = sum(f1s) / len(f1s)
        # Cost from the coldest run: a warm prompt cache from a repeat run would flatter it.
        points.append(Point(model, route, variant, max(costs), mean, ci.low, ci.high, len(dirs)))
    return points


def _dominates(q: Point, p: Point) -> bool:
    """q is at least as good on both axes and strictly better on one."""
    no_worse = q.cost <= p.cost and q.f1 >= p.f1
    better = q.cost < p.cost or q.f1 > p.f1
    return no_worse and better


def pareto_front(points: list[Point]) -> list[Point]:
    """Points not beaten on both cost (lower) and F1 (higher) by any other point."""
    front = [p for p in points if not any(_dominates(q, p) for q in points)]
    return sorted(front, key=lambda p: p.cost)


def render(points: list[Point], out: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FuncFormatter, NullFormatter

    # Zoom to the routes that work; a collapsed route (F1 ~0, e.g. pypdf on scans) is pinned
    # to the bottom edge with an explicit label instead of squashing everything into a sliver.
    on_scale = [p for p in points if p.f1 >= OFF_SCALE_F1] or points
    y_low = 100 * min((p.low for p in on_scale), default=0.5) - 2
    y_high = min(100.0, 100 * max((p.high for p in on_scale), default=1.0) + 2)
    dollars = FuncFormatter(lambda v, _: f"${v:.3g}")

    # Shared x and y: the two panels must be directly comparable.
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharex=True, sharey=True, facecolor=SURFACE)
    for ax, variant in zip(axes, ("clean", "scanned"), strict=True):
        ax.set_facecolor(SURFACE)
        panel = [p for p in points if p.variant == variant]
        front = [p for p in pareto_front(panel) if p.f1 >= OFF_SCALE_F1]
        if len(front) > 1:
            ax.step(
                [p.cost for p in front],
                [100 * p.f1 for p in front],
                where="post",
                color=FRONTIER,
                linewidth=2,
                linestyle="--",
                zorder=1,
            )
        for p in sorted(panel, key=lambda q: (q.cost, q.f1)):
            color = MODEL_COLORS.get(p.model, TEXT_SECONDARY)
            name = ROUTE_LABELS.get(p.route, p.route)
            if p.f1 < OFF_SCALE_F1:
                ax.scatter(
                    p.cost,
                    y_low + 0.4,
                    s=90,
                    marker="v",
                    color=color,
                    edgecolors=SURFACE,
                    linewidths=2,
                    zorder=3,
                    clip_on=False,
                )
                ax.annotate(
                    f"{name}: F1 {100 * p.f1:.0f} (off scale)",
                    (p.cost, y_low + 0.4),
                    xytext=(8, 4),
                    textcoords="offset points",
                    fontsize=9,
                    color=TEXT_PRIMARY,
                )
                continue
            ax.errorbar(
                p.cost,
                100 * p.f1,
                yerr=[[100 * (p.f1 - p.low)], [100 * (p.high - p.f1)]],
                fmt="none",
                ecolor=color,
                elinewidth=1,
                capsize=0,
                alpha=0.6,
                zorder=2,
            )
            ax.scatter(
                p.cost,
                100 * p.f1,
                s=90,
                marker=ROUTE_MARKERS.get(p.route, "o"),
                color=color,
                edgecolors=SURFACE,
                linewidths=2,
                zorder=3,
            )
            model = "" if p.model == "gpt-5.6-luna" else f", {p.model.replace('gpt-5.6-', '')}"
            label = name + model + (f" ({p.runs} runs)" if p.runs > 1 else "")
            offset, align = LABEL_OFFSETS.get(p.route, ((9, 6), "left"))
            ax.annotate(
                label,
                (p.cost, 100 * p.f1),
                xytext=offset,
                textcoords="offset points",
                ha=align,
                fontsize=9,
                color=TEXT_PRIMARY,
            )
        ax.set_xscale("log")
        ax.set_xticks(COST_TICKS)
        ax.xaxis.set_major_formatter(dollars)
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set_title(f"{variant} PDFs", fontsize=11, color=TEXT_PRIMARY, loc="left")
        ax.set_xlabel("total cost per contract, USD (log scale)", fontsize=9, color=TEXT_SECONDARY)
        ax.grid(True, which="major", color=GRID, linewidth=0.8)
        ax.tick_params(colors=TEXT_SECONDARY, labelsize=8, which="both")
        for spine in ax.spines.values():
            spine.set_visible(False)
        if not panel:
            ax.text(
                0.5, 0.5, "no runs yet", transform=ax.transAxes, ha="center", color=TEXT_SECONDARY
            )
    axes[0].set_ylabel("overall micro F1 (95% CI)", fontsize=9, color=TEXT_SECONDARY)
    axes[0].set_ylim(y_low, y_high)
    costs = [p.cost for p in points] or [0.005]
    axes[0].set_xlim(min(costs) / 1.4, max(costs) * 1.6)
    handles = [
        Line2D(
            [], [], marker="o", linestyle="", color=c, markersize=8, label=m.replace("gpt-5.6-", "")
        )
        for m, c in MODEL_COLORS.items()
        if any(p.model == m for p in points)
    ]
    handles.append(
        Line2D([], [], color=FRONTIER, linestyle="--", linewidth=2, label="Pareto frontier")
    )
    fig.legend(handles=handles, loc="upper right", frameon=False, fontsize=9, ncols=len(handles))
    fig.suptitle(title, x=0.01, ha="left", fontsize=12, color=TEXT_PRIMARY)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160, facecolor=SURFACE)
    plt.close(fig)
