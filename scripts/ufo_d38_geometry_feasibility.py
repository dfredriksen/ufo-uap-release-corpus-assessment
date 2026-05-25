from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path


DENSE_TRACK = Path("research/ufo-video-d38-dense-track-dod111689030.csv")
MANUAL_TRACK = Path("research/ufo-video-manual-track-dod111689030.csv")
SUMMARY_OUT = Path("research/ufo-video-d38-geometry-feasibility-summary.csv")
SCENARIO_OUT = Path("research/ufo-video-d38-geometry-feasibility-scenarios.csv")

SOURCE_WIDTH_PX = 1920
MPS_TO_KTS = 1.943844
HFOV_SCENARIOS_DEG = [0.5, 1.0, 2.0, 4.0, 8.0, 10.0, 20.0]
RANGE_SCENARIOS_NM = [1.0, 5.0, 10.0, 20.0, 50.0, 100.0]


def load_dense_rows() -> list[dict]:
    with DENSE_TRACK.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    out = []
    for row in rows:
        out.append(
            {
                "t": float(row["approx_second"]),
                "x": float(row["object_x_full_frame"]),
                "y": float(row["object_y_full_frame"]),
                "phase": row["phase"],
            }
        )
    out.sort(key=lambda row: row["t"])
    return out


def load_manual_rows() -> list[dict]:
    with MANUAL_TRACK.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    out = []
    for row in rows:
        out.append(
            {
                "t": float(row["sample_second"]),
                "x": float(row["manual_x_full_frame"]),
                "y": float(row["manual_y_full_frame"]),
                "phase": row["phase"],
            }
        )
    out.sort(key=lambda row: row["t"])
    return out


def distance(a: dict, b: dict) -> float:
    return math.hypot(float(b["x"]) - float(a["x"]), float(b["y"]) - float(a["y"]))


def stats_for(name: str, rows: list[dict]) -> dict:
    if len(rows) < 2:
        raise ValueError(f"Need at least two rows for {name}")
    start = rows[0]
    end = rows[-1]
    duration = end["t"] - start["t"]
    net_px = distance(start, end)
    total_path = 0.0
    step_rates = []
    for prev, curr in zip(rows, rows[1:]):
        dt = curr["t"] - prev["t"]
        if dt <= 0:
            continue
        step_px = distance(prev, curr)
        total_path += step_px
        step_rates.append(step_px / dt)

    sorted_rates = sorted(step_rates)
    p90 = sorted_rates[int(round(0.90 * (len(sorted_rates) - 1)))]
    p95 = sorted_rates[int(round(0.95 * (len(sorted_rates) - 1)))]
    return {
        "track": name,
        "sample_count": len(rows),
        "start_second": round(start["t"], 3),
        "end_second": round(end["t"], 3),
        "duration_second": round(duration, 3),
        "start_x": round(start["x"], 3),
        "start_y": round(start["y"], 3),
        "end_x": round(end["x"], 3),
        "end_y": round(end["y"], 3),
        "net_displacement_px": round(net_px, 3),
        "net_rate_px_s": round(net_px / duration, 3),
        "total_path_px": round(total_path, 3),
        "path_average_rate_px_s": round(total_path / duration, 3),
        "step_rate_mean_px_s": round(statistics.mean(step_rates), 3),
        "step_rate_median_px_s": round(statistics.median(step_rates), 3),
        "step_rate_p90_px_s": round(p90, 3),
        "step_rate_p95_px_s": round(p95, 3),
        "step_rate_max_px_s": round(max(step_rates), 3),
    }


def filter_phase(rows: list[dict], start: float, end: float) -> list[dict]:
    return [row for row in rows if start <= row["t"] <= end]


def speed_for(px_rate: float, hfov_deg: float, range_nm: float) -> tuple[float, float]:
    angular_rate = px_rate * (math.radians(hfov_deg) / SOURCE_WIDTH_PX)
    speed_mps = angular_rate * range_nm * 1852.0
    return speed_mps, speed_mps * MPS_TO_KTS


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dense = load_dense_rows()
    manual = load_manual_rows()
    summary_rows = [
        stats_for("dense_5fps_full_validated_interval_50_87", dense),
        stats_for("dense_5fps_primary_interval_50_75", filter_phase(dense, 50.0, 75.0)),
        stats_for("dense_5fps_post_zoom_interval_76_87", filter_phase(dense, 76.0, 87.0)),
        stats_for("manual_1fps_full_validated_interval_50_87", manual),
        stats_for("manual_1fps_primary_interval_50_75", filter_phase(manual, 50.0, 75.0)),
        stats_for("manual_1fps_post_zoom_interval_76_87", filter_phase(manual, 76.0, 87.0)),
    ]

    summary_fields = [
        "track",
        "sample_count",
        "start_second",
        "end_second",
        "duration_second",
        "start_x",
        "start_y",
        "end_x",
        "end_y",
        "net_displacement_px",
        "net_rate_px_s",
        "total_path_px",
        "path_average_rate_px_s",
        "step_rate_mean_px_s",
        "step_rate_median_px_s",
        "step_rate_p90_px_s",
        "step_rate_p95_px_s",
        "step_rate_max_px_s",
    ]
    write_csv(SUMMARY_OUT, summary_fields, summary_rows)

    metric_map = {
        "net_rate_px_s": "net start-to-end rate",
        "path_average_rate_px_s": "path-length average rate",
        "step_rate_median_px_s": "median consecutive-step rate",
    }
    scenario_rows: list[dict] = []
    for summary in summary_rows:
        for metric_key, label in metric_map.items():
            px_rate = float(summary[metric_key])
            for hfov in HFOV_SCENARIOS_DEG:
                for range_nm in RANGE_SCENARIOS_NM:
                    speed_mps, speed_kts = speed_for(px_rate, hfov, range_nm)
                    scenario_rows.append(
                        {
                            "track": summary["track"],
                            "rate_metric": metric_key,
                            "rate_label": label,
                            "pixel_rate_px_s": round(px_rate, 3),
                            "assumed_full_frame_hfov_deg": hfov,
                            "assumed_slant_range_nm": range_nm,
                            "source_width_px": SOURCE_WIDTH_PX,
                            "implied_speed_mps": round(speed_mps, 3),
                            "implied_speed_kts": round(speed_kts, 3),
                        }
                    )

    scenario_fields = [
        "track",
        "rate_metric",
        "rate_label",
        "pixel_rate_px_s",
        "assumed_full_frame_hfov_deg",
        "assumed_slant_range_nm",
        "source_width_px",
        "implied_speed_mps",
        "implied_speed_kts",
    ]
    write_csv(SCENARIO_OUT, scenario_fields, scenario_rows)

    for summary in summary_rows:
        print(
            f"{summary['track']}: net_rate={summary['net_rate_px_s']} px/s, "
            f"path_average={summary['path_average_rate_px_s']} px/s, "
            f"median_step={summary['step_rate_median_px_s']} px/s"
        )
    print(f"summary={SUMMARY_OUT}")
    print(f"scenarios={SCENARIO_OUT}")


if __name__ == "__main__":
    main()

