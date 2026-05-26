from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np

from ufo_pr44_overlay_motion_compare import (
    ROOT,
    bright_white_mask,
    components,
    crop_analysis_region,
    cyan_mask,
    draw_box,
    pick_label,
    pick_object,
    pick_reticle_box,
)


DEFAULT_VIDEO = ROOT / "source-files-not-included" / "DOD_111689115.mp4"
DEFAULT_OUT_DIR = ROOT / "research" / "ufo-derived" / "overlay-measurement-audit" / "DOD_111689115-label-survey"
DEFAULT_OUTPUT = ROOT / "research" / "ufo-overlay-measurement-pr44-label-survey.csv"
DEFAULT_INTERVALS = ROOT / "research" / "ufo-overlay-measurement-pr44-label-survey-intervals.csv"


def make_contact_sheet(images: list[np.ndarray], labels: list[str], output: Path, columns: int = 5) -> None:
    if not images:
        return
    tile_w, tile_h = 260, 200
    rows = (len(images) + columns - 1) // columns
    canvas = np.zeros((rows * tile_h, columns * tile_w, 3), dtype=np.uint8)
    for index, img in enumerate(images):
        tile = cv2.resize(img, (tile_w, tile_h), interpolation=cv2.INTER_AREA)
        cv2.putText(tile, labels[index], (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 0, 255), 2, cv2.LINE_AA)
        y = (index // columns) * tile_h
        x = (index % columns) * tile_w
        canvas[y : y + tile_h, x : x + tile_w] = tile
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 94])


def summarize_intervals(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    intervals: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    previous_second: int | None = None
    for row in rows:
        second = int(round(float(row["second"])))
        present = row["label_candidate_present"]
        if current is None or present != current["label_candidate_present"] or previous_second is None or second != previous_second + 1:
            if current is not None:
                current["end_second"] = str(previous_second)
                current["duration_seconds"] = str(int(current["end_second"]) - int(current["start_second"]) + 1)
                intervals.append(current)
            current = {
                "case": row["case"],
                "video": row["video"],
                "record_id": row["record_id"],
                "start_second": str(second),
                "end_second": str(second),
                "duration_seconds": "1",
                "label_candidate_present": present,
                "notes": "Continuous one-second survey interval; label text requires manual review.",
            }
        previous_second = second
    if current is not None and previous_second is not None:
        current["end_second"] = str(previous_second)
        current["duration_seconds"] = str(int(current["end_second"]) - int(current["start_second"]) + 1)
        intervals.append(current)
    return intervals


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Survey PR44 for reticle-associated meter-like label candidates.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--case", default="PR44")
    parser.add_argument("--record-id", default="DOW-UAP-PR44")
    parser.add_argument("--start-second", type=int, default=0)
    parser.add_argument("--end-second", type=int, default=-1)
    parser.add_argument("--sample-step-seconds", type=int, default=1)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--interval-output", type=Path, default=DEFAULT_INTERVALS)
    parser.add_argument("--contact-sheet-window", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.video.exists():
        raise SystemExit(f"Missing source video: {args.video}")

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise SystemExit(f"Could not open source video: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    duration = int(frame_count / fps) if fps else 0
    end_second = duration if args.end_second < 0 else min(args.end_second, duration)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    sheet_images: list[np.ndarray] = []
    sheet_labels: list[str] = []
    sheet_start: int | None = None

    for second in range(args.start_second, end_second + 1, max(args.sample_step_seconds, 1)):
        frame_index = int(round(second * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        crop, x0, y0 = crop_analysis_region(frame)
        cyan_components = components(cyan_mask(crop))
        white_components = components(bright_white_mask(crop))
        box = pick_reticle_box(cyan_components)
        label = pick_label(cyan_components, box) if box else None
        obj = pick_object(white_components, box) if box else None

        annotated = crop.copy()
        draw_box(annotated, box, (0, 255, 255), "reticle")
        draw_box(annotated, label, (255, 255, 0), "label")
        draw_box(annotated, obj, (255, 255, 255), "object")

        if sheet_start is None:
            sheet_start = second
        sheet_images.append(annotated)
        sheet_labels.append(f"{second:03d}s")

        if len(sheet_images) >= args.contact_sheet_window:
            sheet_prefix = args.case.lower()
            sheet_path = args.out_dir / f"{sheet_prefix}_label_survey_{sheet_start:03d}_{second:03d}.jpg"
            make_contact_sheet(sheet_images, sheet_labels, sheet_path)
            sheet_images = []
            sheet_labels = []
            sheet_start = None

        def full(comp: dict[str, float] | None, key: str) -> str:
            if comp is None:
                return ""
            if key in {"x", "cx"}:
                return f"{comp[key] + x0:.2f}"
            if key in {"y", "cy"}:
                return f"{comp[key] + y0:.2f}"
            return f"{comp[key]:.2f}"

        box_cx = box["cx"] + x0 if box else None
        box_cy = box["cy"] + y0 if box else None
        label_cx = label["cx"] + x0 if label else None
        label_cy = label["cy"] + y0 if label else None
        obj_cx = obj["cx"] + x0 if obj else None
        obj_cy = obj["cy"] + y0 if obj else None

        rows.append(
            {
                "case": args.case,
                "video": args.video.name,
                "record_id": args.record_id,
                "second": str(second),
                "frame_index": str(frame_index),
                "reticle_box_present": "yes" if box else "no",
                "label_candidate_present": "yes" if label else "no",
                "object_candidate_present": "yes" if obj else "no",
                "reticle_box_cx": "" if box_cx is None else f"{box_cx:.2f}",
                "reticle_box_cy": "" if box_cy is None else f"{box_cy:.2f}",
                "reticle_box_w": full(box, "w"),
                "reticle_box_h": full(box, "h"),
                "label_cx": "" if label_cx is None else f"{label_cx:.2f}",
                "label_cy": "" if label_cy is None else f"{label_cy:.2f}",
                "label_w": full(label, "w"),
                "label_h": full(label, "h"),
                "label_dx_from_reticle": "" if box_cx is None or label_cx is None else f"{label_cx - box_cx:.2f}",
                "label_dy_from_reticle": "" if box_cy is None or label_cy is None else f"{label_cy - box_cy:.2f}",
                "object_cx": "" if obj_cx is None else f"{obj_cx:.2f}",
                "object_cy": "" if obj_cy is None else f"{obj_cy:.2f}",
                "object_dx_from_reticle": "" if box_cx is None or obj_cx is None else f"{obj_cx - box_cx:.2f}",
                "object_dy_from_reticle": "" if box_cy is None or obj_cy is None else f"{obj_cy - box_cy:.2f}",
                "manual_label_text": "",
                "manual_review_status": "pending" if label else "not_applicable",
                "notes": "One-second reticle/label survey; label text and semantics require manual review." if label else "No reticle-associated label component detected by survey.",
            }
        )

    if sheet_images and sheet_start is not None:
        sheet_prefix = args.case.lower()
        sheet_path = args.out_dir / f"{sheet_prefix}_label_survey_{sheet_start:03d}_{end_second:03d}.jpg"
        make_contact_sheet(sheet_images, sheet_labels, sheet_path)

    cap.release()

    fieldnames = list(rows[0].keys()) if rows else []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    intervals = summarize_intervals(rows)
    interval_fields = list(intervals[0].keys()) if intervals else [
        "case",
        "video",
        "record_id",
        "start_second",
        "end_second",
        "duration_seconds",
        "label_candidate_present",
        "notes",
    ]
    with args.interval_output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=interval_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(intervals)

    print(f"Wrote {len(rows)} survey rows to {args.output}")
    print(f"Wrote {len(intervals)} intervals to {args.interval_output}")
    print(f"Wrote contact sheets to {args.out_dir}")


if __name__ == "__main__":
    main()
