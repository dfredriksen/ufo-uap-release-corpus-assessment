from __future__ import annotations

import csv
import re
from collections import Counter, OrderedDict
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
FIGURES = ROOT / "figures"
PAPER = ROOT / "paper.md"


PALETTE = {
    "blue": "#2F5D8C",
    "teal": "#3B7D7A",
    "green": "#5A7A45",
    "gold": "#C49A3A",
    "red": "#A64E4E",
    "purple": "#6E5A8A",
    "gray": "#5E6470",
    "light": "#F6F7F9",
    "grid": "#D8DDE6",
    "ink": "#1F2933",
    "muted": "#596675",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def text(x: float, y: float, value: str, size: int = 14, weight: str = "400",
         anchor: str = "start", fill: str = PALETTE["ink"]) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Inter, Segoe UI, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">'
        f"{escape(str(value))}</text>"
    )


def rect(x: float, y: float, w: float, h: float, fill: str, rx: float = 0) -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" fill="{fill}" />'


def line(x1: float, y1: float, x2: float, y2: float, stroke: str = PALETTE["grid"], width: float = 1) -> str:
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width:.1f}" />'


def svg_frame(width: int, height: int, title: str, subtitle: str, body: list[str]) -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        f"<title>{escape(title)}</title>",
        rect(0, 0, width, height, "#FFFFFF"),
        text(40, 46, title, size=24, weight="700"),
        text(40, 74, subtitle, size=13, fill=PALETTE["muted"]),
    ]
    parts.extend(body)
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def write_svg(path: Path, svg: str) -> None:
    path.write_text(svg, encoding="utf-8")


def horizontal_bars(path: Path, title: str, subtitle: str, rows: list[tuple[str, int, str]],
                    width: int = 980, left: int = 300) -> None:
    height = 130 + len(rows) * 48
    chart_x = left
    chart_y = 105
    chart_w = width - chart_x - 90
    bar_h = 22
    max_value = max(v for _, v, _ in rows)
    body: list[str] = []
    for i in range(5):
        gx = chart_x + chart_w * i / 4
        body.append(line(gx, chart_y - 10, gx, chart_y + len(rows) * 48 - 10))
        body.append(text(gx, chart_y + len(rows) * 48 + 18, round(max_value * i / 4), size=11, anchor="middle", fill=PALETTE["muted"]))
    for idx, (label, value, color) in enumerate(rows):
        y = chart_y + idx * 48
        body.append(text(40, y + 17, label, size=13, fill=PALETTE["ink"]))
        w = chart_w * value / max_value
        body.append(rect(chart_x, y, w, bar_h, color, rx=3))
        body.append(text(chart_x + w + 10, y + 17, value, size=13, weight="700"))
    write_svg(path, svg_frame(width, height, title, subtitle, body))


def figure_file_types(manifest: list[dict[str, str]]) -> dict[str, int]:
    counts = Counter(row["extension"].lower().lstrip(".").upper() for row in manifest)
    ordered = [("PDF", counts["PDF"], PALETTE["blue"]), ("MP4", counts["MP4"], PALETTE["teal"]),
               ("JPG", counts["JPG"], PALETTE["gold"]), ("PNG", counts["PNG"], PALETTE["purple"])]
    horizontal_bars(
        FIGURES / "fig1-corpus-media-composition.svg",
        "Figure 1. Corpus Media Composition",
        "Source: research/ufo-file-manifest.csv; original release files are not redistributed in this repository.",
        ordered,
        width=920,
        left=170,
    )
    return dict(counts)


def figure_coverage(coverage: list[dict[str, str]]) -> dict[str, int]:
    labels = OrderedDict([
        ("deep_review", "Deep review"),
        ("targeted_review", "Targeted review"),
        ("structured_triage", "Structured triage"),
        ("visual_triage", "Visual triage"),
        ("partial_review", "Partial review"),
    ])
    colors = [PALETTE["blue"], PALETTE["teal"], PALETTE["green"], PALETTE["gold"], PALETTE["red"]]
    counts = Counter(row["coverage_status"] for row in coverage)
    rows = [(labels[k], counts[k], colors[i]) for i, k in enumerate(labels)]
    horizontal_bars(
        FIGURES / "fig2-file-coverage-status.svg",
        "Figure 2. File-Level Coverage Status",
        "Source: research/ufo-file-coverage-map.csv; total coverage rows = 170.",
        rows,
        width=980,
        left=220,
    )
    return dict(counts)


def figure_evidence_ladder(ladder: list[dict[str, str]]) -> dict[str, int]:
    tier_colors = {
        "Tier 1": PALETTE["blue"],
        "Tier 2": PALETTE["teal"],
        "Tier 3": PALETTE["gold"],
        "Tier 4": PALETTE["purple"],
    }
    width = 1180
    row_h = 60
    height = 150 + len(ladder) * row_h
    x_rank = 62
    x_case = 120
    x_class = 430
    x_use = 785
    y0 = 118
    body: list[str] = [
        text(x_rank, y0 - 28, "Rank", size=12, weight="700", fill=PALETTE["muted"]),
        text(x_case, y0 - 28, "Case", size=12, weight="700", fill=PALETTE["muted"]),
        text(x_class, y0 - 28, "Evidence class", size=12, weight="700", fill=PALETTE["muted"]),
        text(x_use, y0 - 28, "Use in report", size=12, weight="700", fill=PALETTE["muted"]),
        line(40, y0 - 16, width - 40, y0 - 16, stroke=PALETTE["grid"], width=1.2),
    ]
    tier_counts = Counter()
    for idx, row in enumerate(ladder):
        y = y0 + idx * row_h
        tier = row["tier"]
        tier_counts[tier] += 1
        if idx % 2 == 0:
            body.append(rect(40, y - 22, width - 80, row_h, PALETTE["light"]))
        body.append(f'<circle cx="{x_rank:.1f}" cy="{y:.1f}" r="13" fill="{tier_colors[tier]}" />')
        body.append(text(x_rank, y + 5, row["rank"], size=11, weight="700", anchor="middle", fill="#FFFFFF"))
        body.append(text(x_case, y + 5, row["item"], size=12))
        for j, wrapped in enumerate(wrap(row["evidence_class"], width=46)[:2]):
            body.append(text(x_class, y - 3 + j * 15, wrapped, size=10, fill=PALETTE["ink"]))
        for j, wrapped in enumerate(wrap(row["main_value"], width=58)[:2]):
            body.append(text(x_use, y - 3 + j * 15, wrapped, size=10, fill=PALETTE["muted"]))
    legend_y = height - 44
    x = 40
    for tier, color in tier_colors.items():
        body.append(rect(x, legend_y - 13, 18, 18, color, rx=3))
        body.append(text(x + 26, legend_y + 1, f"{tier}: {tier_counts[tier]} rows", size=12, fill=PALETTE["muted"]))
        x += 180
    write_svg(
        FIGURES / "fig3-evidence-ladder-ranking.svg",
        svg_frame(
            width,
            height,
            "Figure 3. Evidence Ladder Ranking",
            "Source: research/ufo-evidence-ladder.csv; ranking measures analytic utility, not strangeness.",
            body,
        ),
    )
    return dict(tier_counts)


def parse_source_priorities(paper_text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_table = False
    for raw in paper_text.splitlines():
        if raw.startswith("| Priority | Case | Requested material |"):
            in_table = True
            continue
        if in_table and raw.startswith("|---"):
            continue
        if in_table:
            if not raw.startswith("|"):
                break
            cols = [c.strip().strip("`") for c in raw.strip("|").split("|")]
            if len(cols) == 3 and cols[0].isdigit():
                rows.append({"priority": cols[0], "case": cols[1], "requested_material": cols[2]})
    return rows


def figure_source_requests(source_requests: list[dict[str, str]]) -> None:
    width = 1120
    height = 610
    y0 = 118
    row_h = 55
    x_rank = 65
    x_case = 132
    x_need = 265
    body: list[str] = [
        text(x_rank, y0 - 28, "Priority", size=12, weight="700", fill=PALETTE["muted"]),
        text(x_case, y0 - 28, "Case", size=12, weight="700", fill=PALETTE["muted"]),
        text(x_need, y0 - 28, "Requested material", size=12, weight="700", fill=PALETTE["muted"]),
        line(40, y0 - 16, width - 40, y0 - 16, stroke=PALETTE["grid"], width=1.2),
    ]
    colors = [PALETTE["red"], PALETTE["red"], PALETTE["blue"], PALETTE["blue"],
              PALETTE["teal"], PALETTE["teal"], PALETTE["gold"], PALETTE["purple"]]
    for idx, row in enumerate(source_requests):
        y = y0 + idx * row_h
        if idx % 2 == 0:
            body.append(rect(40, y - 24, width - 80, row_h, PALETTE["light"]))
        body.append(f'<circle cx="{x_rank:.1f}" cy="{y:.1f}" r="15" fill="{colors[idx]}" />')
        body.append(text(x_rank, y + 5, row["priority"], size=12, weight="700", anchor="middle", fill="#FFFFFF"))
        body.append(text(x_case, y + 5, row["case"], size=13, weight="700"))
        for j, wrapped in enumerate(wrap(row["requested_material"], width=105)[:2]):
            body.append(text(x_need, y + 1 + j * 16, wrapped, size=11, fill=PALETTE["muted"]))
    write_svg(
        FIGURES / "fig4-source-request-priorities.svg",
        svg_frame(
            width,
            height,
            "Figure 4. Source-Request Priorities",
            "Source: Source-Request Priorities table in paper.md; priority 1 is highest.",
            body,
        ),
    )


def theme_counts(ladder: list[dict[str, str]]) -> list[dict[str, object]]:
    themes = OrderedDict([
        ("Public video linkage", "tier in Tier 1 or Tier 3"),
        ("Document-only evidence", "evidence_class contains Document-only"),
        ("Kinematic/data limits", "row text contains telemetry/FOV/range/physical/kinematic/speed/platform/slant"),
        ("Sensor/IR/radar context", "row text contains sensor/IR/SWIR/FMV/radar/target-pod/EO/IR"),
        ("Source-index conflicts", "row text contains metadata/label/mismatch/conflict/DVIDS says"),
        ("Conventional/confound caveats", "row text contains conventional/possible/glare/bird/aircraft/balloon/reflection/cloud/jamming/EW"),
        ("Pattern/narrative lower weight", "row text contains pattern/cluster/narrative/briefing/slide"),
    ])
    regexes = {
        "Kinematic/data limits": [r"telemetry", r"\bFOV\b", r"range", r"physical", r"kinematic", r"speed", r"platform", r"slant"],
        "Sensor/IR/radar context": [r"sensor", r"\bIR\b", r"SWIR", r"FMV", r"radar", r"target-pod", r"EO/IR"],
        "Source-index conflicts": [r"metadata", r"label", r"mismatch", r"conflict", r"DVIDS says"],
        "Conventional/confound caveats": [r"conventional", r"possible", r"glare", r"bird", r"aircraft", r"balloon", r"reflection", r"cloud", r"jamming", r"\bEW\b"],
        "Pattern/narrative lower weight": [r"pattern", r"cluster", r"narrative", r"briefing", r"slide"],
    }
    rows: list[dict[str, object]] = []
    for theme, method in themes.items():
        matching: list[str] = []
        for row in ladder:
            combined = " ".join(
                row[field]
                for field in [
                    "tier",
                    "item",
                    "case_group",
                    "evidence_class",
                    "pairing_status",
                    "confidence",
                    "main_value",
                    "main_caveat",
                    "next_action",
                ]
            )
            if theme == "Public video linkage":
                matched = row["tier"] in {"Tier 1", "Tier 3"}
            elif theme == "Document-only evidence":
                matched = "Document-only" in row["evidence_class"]
            else:
                matched = any(re.search(pattern, combined, flags=re.IGNORECASE) for pattern in regexes[theme])
            if matched:
                matching.append(row["item"])
        rows.append({
            "theme": theme,
            "evidence_ladder_rows": len(matching),
            "matching_items": "; ".join(matching),
            "method": method,
        })
    return rows


def count_themes(texts: pd.Series, theme_rules: dict[str, list[str]]) -> pd.Series:
    joined = texts.fillna("").astype(str).str.lower()
    counts = {}
    for theme, patterns in theme_rules.items():
        regex = re.compile("|".join(patterns), re.I)
        counts[theme] = int(joined.apply(lambda value: bool(regex.search(value))).sum())
    return pd.Series(counts).sort_values(ascending=False)


def figure_themes(theme_rows: list[dict[str, object]]) -> None:
    rows = [(str(r["theme"]), int(r["evidence_ladder_rows"]), color) for r, color in zip(
        theme_rows,
        [PALETTE["blue"], PALETTE["teal"], PALETTE["red"], PALETTE["green"], PALETTE["purple"], PALETTE["gold"], PALETTE["gray"]],
    )]
    horizontal_bars(
        FIGURES / "fig5-evidence-ladder-theme-frequency.svg",
        "Figure 5. Common Themes In Ranked Evidence Rows",
        "Source: transparent keyword scan across research/ufo-evidence-ladder.csv; illustrative, not proof of prevalence.",
        rows,
        width=1080,
        left=300,
    )


def figure_release_02_theme_summary() -> None:
    files = [
        RESEARCH / "ufo-release-02-synthesis.md",
        RESEARCH / "ufo-release-02-source-review.md",
        RESEARCH / "ufo-release-02-nonvideo-review.md",
        RESEARCH / "ufo-release-02-video-review.md",
    ]
    texts = []
    for path in files:
        if path.exists():
            texts.append(path.read_text(encoding="utf-8"))
    joined = pd.Series(texts)

    theme_rules = {
        "Standalone release family": [r"standalone release family", r"second tranche", r"broadens the release landscape"],
        "Over-water / modern sensor lanes": [r"over-water", r"sensor", r"flir", r"swir", r"formation", r"multi-contact"],
        "Historical / archive material": [r"historical", r"sandia", r"green fireball", r"archive", r"cia"],
        "Narrative / provenance lanes": [r"narrative", r"provenance", r"image/provenance"],
        "Control / caveat material": [r"control", r"caveat", r"control-oriented", r"no new hard pairings"],
        "Duplicate / altered / same-title": [r"duplicate", r"same-title", r"digitally altered"],
        "Source-index / label hygiene": [r"mismatch", r"label", r"source-index", r"corrected report-content match"],
        "No claim-ceiling change": [r"claim ceiling", r"does not raise", r"broadens breadth"],
    }
    counts = count_themes(joined, theme_rules).sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(11.5, 6.6))
    bars = ax.barh(list(range(len(counts)))[::-1], counts.values, color="#edc948")
    ax.set_title("Supplemental Figure 6. Release 02 Theme Summary", pad=12, weight="bold")
    ax.set_xlabel("Review notes containing theme")
    ax.set_yticks(list(range(len(counts)))[::-1])
    ax.set_yticklabels(["\n".join(wrap(label, 32)) for label in counts.index], fontsize=9)
    ax.set_xlim(0, max(counts.values) * 1.25 if len(counts) else 1)
    ax.grid(axis="x", alpha=0.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    for bar, value in zip(bars, counts.values):
        ax.text(bar.get_width() + 0.12, bar.get_y() + bar.get_height() / 2, str(int(value)), va="center", fontsize=8)
    fig.tight_layout()
    svg_path = FIGURES / "fig6-release-02-theme-summary.svg"
    fig.savefig(svg_path, format="svg", bbox_inches="tight")
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)


def validation_note(summary: dict[str, object]) -> str:
    return f"""# Publication Figure Validation

Generated: 2026-05-15

This note records the source data and validation checks for the publication figures. The figures are generated by `scripts/generate_publication_figures.py` using the dependencies listed in `requirements.txt`.

## Figure Sources

| Figure | File | Source | Validation check |
|---|---|---|---|
| Figure 1 | `figures/fig1-corpus-media-composition.svg` | `research/ufo-file-manifest.csv` | Extension counts sum to `{summary['manifest_total']}` files. |
| Figure 2 | `figures/fig2-file-coverage-status.svg` | `research/ufo-file-coverage-map.csv` | Coverage-status counts sum to `{summary['coverage_total']}` rows. |
| Figure 3 | `figures/fig3-evidence-ladder-ranking.svg` | `research/ufo-evidence-ladder.csv` | Evidence ladder contains `{summary['ladder_total']}` ranked rows. |
| Figure 4 | `figures/fig4-source-request-priorities.svg` | `paper.md` Source-Request Priorities table | Parsed `{summary['source_request_total']}` priority rows from the paper. |
| Figure 5 | `figures/fig5-evidence-ladder-theme-frequency.svg` | `research/ufo-evidence-ladder.csv` | Theme counts are reproducible in `figures/theme-frequency.csv`. |
| Figure 6 | `figures/fig6-release-02-theme-summary.svg` | `research/ufo-release-02-synthesis.md`, `research/ufo-release-02-source-review.md`, `research/ufo-release-02-nonvideo-review.md`, `research/ufo-release-02-video-review.md` | Release 02 theme summary generated from tranche review notes. |

## Checked Counts

Media composition:

{summary['media_counts']}

Coverage status:

{summary['coverage_counts']}

Evidence tiers:

{summary['tier_counts']}

## Caveat On Theme Frequency

Figure 5 is a controlled keyword-frequency visualization across the `18` ranked evidence-ladder rows. It is included to show recurrent analytic themes, not to estimate real-world UAP prevalence or object frequency.

Supplemental Figure 6 summarizes recurring themes in the Release 02 synthesis and review notes without changing the report's claim ceiling.
"""


def main() -> None:
    FIGURES.mkdir(exist_ok=True)
    manifest = read_csv(RESEARCH / "ufo-file-manifest.csv")
    coverage = read_csv(RESEARCH / "ufo-file-coverage-map.csv")
    ladder = read_csv(RESEARCH / "ufo-evidence-ladder.csv")
    paper_text = PAPER.read_text(encoding="utf-8")

    media = figure_file_types(manifest)
    coverage_counts = figure_coverage(coverage)
    tier_counts = figure_evidence_ladder(ladder)
    source_requests = parse_source_priorities(paper_text)
    figure_source_requests(source_requests)
    theme_rows = theme_counts(ladder)
    write_csv(FIGURES / "theme-frequency.csv", theme_rows)
    figure_themes(theme_rows)
    figure_release_02_theme_summary()
    write_csv(FIGURES / "source-request-priorities.csv", source_requests)

    assert sum(media.values()) == len(manifest), "media counts do not sum to manifest rows"
    assert sum(coverage_counts.values()) == len(coverage), "coverage counts do not sum to coverage rows"
    assert len(ladder) == 18, "evidence ladder row count changed"
    assert len(source_requests) == 8, "source-request row count changed"

    summary = {
        "manifest_total": len(manifest),
        "coverage_total": len(coverage),
        "ladder_total": len(ladder),
        "source_request_total": len(source_requests),
        "media_counts": "\n".join(f"- `{k}`: `{v}`" for k, v in sorted(media.items())),
        "coverage_counts": "\n".join(f"- `{k}`: `{v}`" for k, v in sorted(coverage_counts.items())),
        "tier_counts": "\n".join(f"- `{k}`: `{v}`" for k, v in sorted(tier_counts.items())),
    }
    (FIGURES / "figure-validation.md").write_text(validation_note(summary), encoding="utf-8")


if __name__ == "__main__":
    main()

