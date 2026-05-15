from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path


TRACK = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr34-d33-manual-track-dod111689011.csv")
TURN_EVENTS = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-image-plane-turn-events.csv")
SUMMARY_OUT = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-geometry-feasibility-summary.csv")
RANGE_SCENARIO_OUT = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-geometry-feasibility-range-scenarios.csv")
SPEED_SCENARIO_OUT = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-geometry-feasibility-speed-scenarios.csv")

SOURCE_WIDTH_PX = 1920
MPH_TO_MPS = 0.44704
MPS_TO_MPH = 2.2369362920544
MPS_TO_KTS = 1.943844
TARGET_SPEED_MPH = 80.0
TARGET_SPEED_MPS = TARGET_SPEED_MPH * MPH_TO_MPS
HFOV_SCENARIOS_DEG = [0.5, 1.0, 2.0, 4.0, 8.0, 10.0, 20.0]
RANGE_SCENARIOS_NM = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]


def load_track() -> list[dict]:
    with TRACK.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    out: list[dict] = []
    for row in rows:
        out.append(
            {
                "t": float(row["approx_second"]),
                "x": float(row["manual_x_full_frame"]),
                "y": float(row["manual_y_full_frame"]),
                "phase": row["phase"],
                "manual_status": row["manual_status"],
                "manual_quality": row["manual_quality"],
            }
        )
    out.sort(key=lambda item: item["t"])
    return out


def load_turn_events() -> list[dict]:
    with TURN_EVENTS.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def distance(a: dict, b: dict) -> float:
    return math.hypot(float(b["x"]) - float(a["x"]), float(b["y"]) - float(a["y"]))


def percentile(sorted_values: list[float], percentile_value: float) -> float:
    if not sorted_values:
        return 0.0
    index = int(round(percentile_value * (len(sorted_values) - 1)))
    return sorted_values[index]


def track_stats(name: str, rows: list[dict], note: str) -> dict:
    if len(rows) < 2:
        raise ValueError(f"Need at least two rows for {name}")

    rows = sorted(rows, key=lambda item: item["t"])
    start = rows[0]
    end = rows[-1]
    duration = end["t"] - start["t"]
    net_px = distance(start, end)
    total_path = 0.0
    step_rates: list[float] = []
    interpolation_step_count = 0
    accepted_step_count = 0
    for prev, curr in zip(rows, rows[1:]):
        dt = curr["t"] - prev["t"]
        if dt <= 0:
            continue
        step_px = distance(prev, curr)
        total_path += step_px
        step_rates.append(step_px / dt)
        if curr["manual_status"] == "interpolated_detector_dropout" or prev["manual_status"] == "interpolated_detector_dropout":
            interpolation_step_count += 1
        else:
            accepted_step_count += 1

    sorted_rates = sorted(step_rates)
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
        "step_rate_p90_px_s": round(percentile(sorted_rates, 0.90), 3),
        "step_rate_p95_px_s": round(percentile(sorted_rates, 0.95), 3),
        "step_rate_max_px_s": round(max(step_rates), 3),
        "accepted_step_count": accepted_step_count,
        "interpolation_involved_step_count": interpolation_step_count,
        "note": note,
    }


def by_phase(rows: list[dict], phase: str) -> list[dict]:
    return [row for row in rows if row["phase"] == phase]


def accepted_only(rows: list[dict]) -> list[dict]:
    return [row for row in rows if row["manual_status"] == "accepted_detector_mark"]


def angular_rate(px_rate: float, hfov_deg: float) -> float:
    return px_rate * (math.radians(hfov_deg) / SOURCE_WIDTH_PX)


def implied_range_for_speed(px_rate: float, hfov_deg: float) -> tuple[float, float, float]:
    rate_rad_s = angular_rate(px_rate, hfov_deg)
    if rate_rad_s <= 0:
        return rate_rad_s, 0.0, 0.0
    range_m = TARGET_SPEED_MPS / rate_rad_s
    return rate_rad_s, range_m, range_m / 1852.0


def implied_speed_for_range(px_rate: float, hfov_deg: float, range_nm: float) -> tuple[float, float, float]:
    rate_rad_s = angular_rate(px_rate, hfov_deg)
    speed_mps = rate_rad_s * range_nm * 1852.0
    return speed_mps, speed_mps * MPS_TO_MPH, speed_mps * MPS_TO_KTS


def turn_angular_rate(event: dict, hfov_deg: float) -> float:
    heading_delta_rad = math.radians(float(event["heading_delta_deg"]))
    span_seconds = float(event["vector_span_seconds"])
    return heading_delta_rad / span_seconds if span_seconds > 0 else 0.0


def turn_radius_for_80mph(event: dict) -> float:
    omega = math.radians(float(event["heading_delta_deg"])) / float(event["vector_span_seconds"])
    if omega <= 0:
        return 0.0
    return TARGET_SPEED_MPS / omega


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = load_track()
    turns = load_turn_events()
    summaries = [
        track_stats(
            "manual_review_track_all_4_59",
            rows,
            "cleaned continuity track; includes interpolated detector dropouts after top-edge artifact rejection",
        ),
        track_stats(
            "manual_review_accepted_marks_only_4_59",
            accepted_only(rows),
            "accepted detector-centered marks only; skips interpolated dropout rows",
        ),
    ]

    for phase in ["entry from bottom-left quarter", "horizontal back-and-forth tracking", "generally centered in FOV"]:
        phase_rows = by_phase(rows, phase)
        if len(phase_rows) >= 2:
            summaries.append(track_stats(f"phase_all: {phase}", phase_rows, "phase-specific cleaned continuity track"))
        phase_accepted = accepted_only(phase_rows)
        if len(phase_accepted) >= 2:
            summaries.append(track_stats(f"phase_accepted_only: {phase}", phase_accepted, "phase-specific accepted marks only"))

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
        "accepted_step_count",
        "interpolation_involved_step_count",
        "note",
    ]
    write_csv(SUMMARY_OUT, summary_fields, summaries)

    metric_map = {
        "net_rate_px_s": "net start-to-end rate",
        "path_average_rate_px_s": "path-length average rate",
        "step_rate_median_px_s": "median consecutive-step rate",
        "step_rate_p95_px_s": "p95 consecutive-step rate",
    }

    range_rows: list[dict] = []
    speed_rows: list[dict] = []
    for summary in summaries:
        for metric_key, label in metric_map.items():
            px_rate = float(summary[metric_key])
            for hfov in HFOV_SCENARIOS_DEG:
                rate_rad_s, range_m, range_nm = implied_range_for_speed(px_rate, hfov)
                range_rows.append(
                    {
                        "track": summary["track"],
                        "rate_metric": metric_key,
                        "rate_label": label,
                        "pixel_rate_px_s": round(px_rate, 3),
                        "target_speed_mph": TARGET_SPEED_MPH,
                        "target_speed_mps": round(TARGET_SPEED_MPS, 3),
                        "assumed_full_frame_hfov_deg": hfov,
                        "source_width_px": SOURCE_WIDTH_PX,
                        "angular_rate_rad_s": round(rate_rad_s, 9),
                        "implied_slant_range_for_80mph_m": round(range_m, 1),
                        "implied_slant_range_for_80mph_nm": round(range_nm, 3),
                    }
                )
                for range_scenario_nm in RANGE_SCENARIOS_NM:
                    speed_mps, speed_mph, speed_kts = implied_speed_for_range(px_rate, hfov, range_scenario_nm)
                    speed_rows.append(
                        {
                            "track": summary["track"],
                            "rate_metric": metric_key,
                            "rate_label": label,
                            "pixel_rate_px_s": round(px_rate, 3),
                            "assumed_full_frame_hfov_deg": hfov,
                            "assumed_slant_range_nm": range_scenario_nm,
                            "source_width_px": SOURCE_WIDTH_PX,
                            "implied_speed_mps": round(speed_mps, 3),
                            "implied_speed_mph": round(speed_mph, 3),
                            "implied_speed_kts": round(speed_kts, 3),
                        }
                    )

    range_fields = [
        "track",
        "rate_metric",
        "rate_label",
        "pixel_rate_px_s",
        "target_speed_mph",
        "target_speed_mps",
        "assumed_full_frame_hfov_deg",
        "source_width_px",
        "angular_rate_rad_s",
        "implied_slant_range_for_80mph_m",
        "implied_slant_range_for_80mph_nm",
    ]
    write_csv(RANGE_SCENARIO_OUT, range_fields, range_rows)

    speed_fields = [
        "track",
        "rate_metric",
        "rate_label",
        "pixel_rate_px_s",
        "assumed_full_frame_hfov_deg",
        "assumed_slant_range_nm",
        "source_width_px",
        "implied_speed_mps",
        "implied_speed_mph",
        "implied_speed_kts",
    ]
    write_csv(SPEED_SCENARIO_OUT, speed_fields, speed_rows)

    turn_rows: list[dict] = []
    for event in turns:
        radius_m = turn_radius_for_80mph(event)
        turn_rows.append(
            {
                "track": "manual_review_track_all_4_59",
                "event_id": event["event_id"],
                "approx_second": event["approx_second"],
                "heading_delta_deg": event["heading_delta_deg"],
                "vector_span_seconds": event["vector_span_seconds"],
                "turn_rate_deg_s": round(float(event["heading_delta_deg"]) / float(event["vector_span_seconds"]), 3),
                "implied_turn_radius_at_80mph_m": round(radius_m, 1),
                "implied_turn_radius_at_80mph_nm": round(radius_m / 1852.0, 4),
                "note": "image-plane heading-change event; not a physical turn radius without sensor/platform geometry",
            }
        )

    turn_out = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-geometry-feasibility-turn-radius-scenarios.csv")
    write_csv(
        turn_out,
        [
            "track",
            "event_id",
            "approx_second",
            "heading_delta_deg",
            "vector_span_seconds",
            "turn_rate_deg_s",
            "implied_turn_radius_at_80mph_m",
            "implied_turn_radius_at_80mph_nm",
            "note",
        ],
        turn_rows,
    )

    for summary in summaries:
        print(
            f"{summary['track']}: net={summary['net_rate_px_s']} px/s, "
            f"path={summary['path_average_rate_px_s']} px/s, "
            f"median={summary['step_rate_median_px_s']} px/s"
        )
    print(f"target_speed_mph={TARGET_SPEED_MPH} target_speed_mps={round(TARGET_SPEED_MPS, 3)}")
    print(f"summary={SUMMARY_OUT}")
    print(f"range_scenarios={RANGE_SCENARIO_OUT}")
    print(f"speed_scenarios={SPEED_SCENARIO_OUT}")
    print(f"turn_scenarios={turn_out}")


if __name__ == "__main__":
    main()
