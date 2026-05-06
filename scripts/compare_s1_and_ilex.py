import csv
from pathlib import Path

root_dir = Path("/Users/eldena/Desktop/UZH/2026_Spring/sarah/smile1_data")
s1_csv = root_dir / "s1_durations.csv"
ilex_csv = root_dir / "ilex_time_spans_with_seconds.csv"
out_csv = root_dir / "s1_ilex_comparison.csv"

s1_data = {}
with open(s1_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        s1_data[row["folder"]] = row

ilex_data = {}
with open(ilex_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ilex_data[row["folder"]] = row

all_folders = sorted(set(s1_data) | set(ilex_data))

rows = []
for folder in all_folders:
    s1_row = s1_data.get(folder, {})
    ilex_row = ilex_data.get(folder, {})

    s1_duration = s1_row.get("s1_duration_s", "")
    ilex_span = ilex_row.get("span_s", "")

    diff = ""
    if s1_duration and ilex_span:
        try:
            diff = float(s1_duration) - float(ilex_span)
        except ValueError:
            diff = ""

    rows.append([
        folder,
        s1_row.get("s1_file", ""),
        s1_duration,
        ilex_row.get("ilex_file", ""),
        ilex_row.get("earliest_tc", ""),
        ilex_row.get("latest_tc", ""),
        ilex_span,
        diff,
    ])

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "folder",
        "s1_file",
        "s1_duration_s",
        "ilex_file",
        "earliest_tc",
        "latest_tc",
        "ilex_span_s",
        "duration_minus_span_s",
    ])
    writer.writerows(rows)

print(f"Saved to: {out_csv}")