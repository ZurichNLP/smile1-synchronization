import csv
from pathlib import Path

root_dir = Path("/Users/eldena/Desktop/UZH/2026_Spring/sarah/smile1_data")
in_csv = root_dir / "ilex_time_spans.csv"
out_csv = root_dir / "ilex_time_spans_with_seconds.csv"

FPS = 30  # 当前工作假设

def tc_to_seconds(tc: str, fps: int = FPS) -> float:
    hh, mm, ss, ff = map(int, tc.split(":"))
    return hh * 3600 + mm * 60 + ss + ff / fps

rows_out = []

with open(in_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        earliest = row["earliest_tc"]
        latest = row["latest_tc"]
        note = row["note"]

        span_s = ""
        if earliest and latest:
            span_s = tc_to_seconds(latest) - tc_to_seconds(earliest)

        rows_out.append([
            row["folder"],
            row["ilex_file"],
            earliest,
            latest,
            span_s,
            note,
        ])

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["folder", "ilex_file", "earliest_tc", "latest_tc", "span_s", "note"])
    writer.writerows(rows_out)

print(f"Saved to: {out_csv}")