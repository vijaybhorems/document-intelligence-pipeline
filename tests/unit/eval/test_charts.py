from pathlib import Path

from dip.eval.charts import Point, pareto_front, render


def _p(route: str, cost: float, f1: float, variant: str = "clean") -> Point:
    return Point("gpt-5.6-luna", route, variant, cost, f1, f1 - 0.02, f1 + 0.02, 1)


def test_pareto_front_keeps_only_undominated_points() -> None:
    cheap_ok = _p("pypdf", 0.004, 0.80)
    dear_best = _p("multimodal", 0.03, 0.85)
    dominated = _p("docling", 0.01, 0.79)  # costs more than pypdf and scores lower
    tie_cost_better = _p("txt", 0.004, 0.82)  # same cost as pypdf, higher F1: beats it

    front = pareto_front([cheap_ok, dear_best, dominated, tie_cost_better])

    assert front == [tie_cost_better, dear_best]


def test_render_writes_a_png_even_with_an_empty_panel(tmp_path: Path) -> None:
    out = tmp_path / "pareto.png"

    render([_p("txt", 0.006, 0.83)], out, "test")

    assert out.read_bytes()[:8] == bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
