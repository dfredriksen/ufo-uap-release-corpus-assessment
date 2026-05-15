from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path


DENSE_TRACK = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dense-track-dod111688964.csv")
MANUAL_TRACK = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-manual-track-dod111688964.csv")
SUMMARY_OUT = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-geometry-feasibility-summary.csv")
SCENARIO_OUT = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-geometry-feasibility-scenarios.csv")

SOURCE_WIDTH_PX = 1920
KNOT_TO_MPS = 0.514444
TARGET_SPEED_KTS = 140.0
TARGET_SPEED_MPS = TARGET_SPEED_KTS * KNOT_TO_MPS
HFOV_SCENARIOS_DEG = [0.5, 1.0, 2.0, 4.0, 8.0, 10.0, 20.0]


def load_xy(path: Path, time_key: str, x_key: str, y_key: str) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for row in rows:
        out.append(
            {
                "t": float(row[time_key]),
                "x": float(row[x_key]),
                "y": float(row[y_key]),
            }
        )
    out.sort(key=lambda row: row["t"])
    return out


def distance(a: dict, b: dict) -> float:
    return math.hypot(float(b["x"]) - float(a["x"]), float(b["y"]) - float(a["y"]))


def track_stats(name: str, rows: list[dict]) -> dict:
    if len(rows) < 2:
        raise ValueError(f"Need at least two rows for {name}")

    start = rows[0]
    end = rows[-1]
    duration = end["t"] - start["t"]
    net_px = distance(start, end)
    step_rates = []
    total_path = 0.0
    for prev, curr in zip(rows, rows[1:]):
        dt = curr["t"] - prev["t"]
        if dt <= 0:
            continue
        step_px = distance(prev, curr)
        total_path += step_px
        step_rates.append(step_px / dt)

    step_rates_sorted = sorted(step_rates)
    p90 = step_rates_sorted[int(round(0.90 * (len(step_rates_sorted) - 1)))]
    p95 = step_rates_sorted[int(round(0.95 * (len(step_rates_sorted) - 1)))]
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


def implied_range_for_speed(px_rate: float, hfov_deg: float) -> tuple[float, float, float]:
    hfov_rad = math.radians(hfov_deg)
    radians_per_pixel = hfov_rad / SOURCE_WIDTH_PX
    angular_rate = px_rate * radians_per_pixel
    if angular_rate <= 0:
        return 0.0, 0.0, 0.0
    range_m = TARGET_SPEED_MPS / angular_rate
    range_nm = range_m / 1852.0
    return angular_rate, range_m, range_nm


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dense_rows = load_xy(DENSE_TRACK, "approx_second", "object_x", "object_y")
    manual_rows = load_xy(MANUAL_TRACK, "approx_second", "object_x", "object_y")
    summaries = [
        track_stats("dense_5fps_audit_track", dense_rows),
        track_stats("manual_1fps_control_track", manual_rows),
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
    write_csv(SUMMARY_OUT, summary_fields, summaries)

    scenario_rows: list[dict] = []
    metric_map = {
        "net_rate_px_s": "net start-to-end rate",
        "path_average_rate_px_s": "path-length average rate",
        "step_rate_median_px_s": "median consecutive-step rate",
        "step_rate_p95_px_s": "p95 consecutive-step rate",
    }
    for summary in summaries:
        for metric_key, metric_label in metric_map.items():
            px_rate = float(summary[metric_key])
            for hfov_deg in HFOV_SCENARIOS_DEG:
                angular_rate, range_m, range_nm = implied_range_for_speed(px_rate, hfov_deg)
                scenario_rows.append(
                    {
                        "track": summary["track"],
                        "rate_metric": metric_key,
                        "rate_label": metric_label,
                        "pixel_rate_px_s": round(px_rate, 3),
                        "assumed_full_frame_hfov_deg": hfov_deg,
                        "source_width_px": SOURCE_WIDTH_PX,
                        "angular_rate_rad_s": round(angular_rate, 8),
                        "implied_slant_range_for_140kt_m": round(range_m, 1),
                        "implied_slant_range_for_140kt_nm": round(range_nm, 3),
                    }
                )

    scenario_fields = [
        "track",
        "rate_metric",
        "rate_label",
        "pixel_rate_px_s",
        "assumed_full_frame_hfov_deg",
        "source_width_px",
        "angular_rate_rad_s",
        "implied_slant_range_for_140kt_m",
        "implied_slant_range_for_140kt_nm",
    ]
    write_csv(SCENARIO_OUT, scenario_fields, scenario_rows)

    for summary in summaries:
        print(
            f"{summary['track']}: net_rate={summary['net_rate_px_s']} px/s, "
            f"path_average={summary['path_average_rate_px_s']} px/s, "
            f"median_step={summary['step_rate_median_px_s']} px/s"
        )
    print(f"target_speed_mps={round(TARGET_SPEED_MPS, 3)}")
    print(f"summary={SUMMARY_OUT}")
    print(f"scenarios={SCENARIO_OUT}")


if __name__ == "__main__":
    main()
