import re
from pathlib import Path
import csv

root_dir = Path("/Users/eldena/Desktop/UZH/2026_Spring/sarah/smile1_data")
output_csv = root_dir / "kinect_gopro1_offsets.csv"

rows = []

for startms_path in root_dir.rglob("StartMS.txt"):
    folder = startms_path.parent
    startms2_path = folder / "StartMS2.txt"

    if not startms2_path.exists():
        print(f"[SKIP] Missing StartMS2.txt in {folder}")
        continue

    starts1 = {}
    starts2 = {}

    # Read StartMS.txt -> Kinect
    with open(startms_path, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r'(.+?) started recording at: (\d+)', line.strip())
            if m:
                cam = m.group(1)
                t = int(m.group(2))
                starts1[cam] = t

    # Read StartMS2.txt -> GoPro1
    with open(startms2_path, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r'(.+?) started recording at: (\d+)', line.strip())
            if m:
                cam = m.group(1)
                t = int(m.group(2))
                starts2[cam] = t

    if "Kinect" not in starts1:
        print(f"[SKIP] Missing Kinect in {startms_path}")
        continue

    if "GoPro1" not in starts2:
        print(f"[SKIP] Missing GoPro1 in {startms2_path}")
        continue

    kinect_start = starts1["Kinect"]
    gopro1_start = starts2["GoPro1"]

    offset_ms = kinect_start - gopro1_start
    offset_s = offset_ms / 1000.0

    rel_folder = folder.relative_to(root_dir)

    print(f"[OK] {rel_folder} -> offset = {offset_ms} ms ({offset_s:.3f} s)")

    rows.append([
        str(rel_folder),
        kinect_start,
        gopro1_start,
        offset_ms,
        offset_s,
    ])

with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "folder",
        "Kinect_start",
        "GoPro1_start",
        "offset_ms",
        "offset_s",
    ])
    writer.writerows(rows)

print(f"\nSaved results to: {output_csv}")