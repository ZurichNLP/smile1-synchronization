import csv
import json
import subprocess
from pathlib import Path

root = Path("/shares/iict-sp2.ebling.cl.uzh/visuoacoustic_slr/glossed/continuous/SMILE1_SRT_participants")
out_csv = Path.home() / "smile_sync_check" / "s1_fps_check.csv"

rows = []

for s1_path in sorted(root.rglob("*_S1.mp4")):
    rel_folder = s1_path.parent.relative_to(root)

    cmd = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_streams",
        "-show_format",
        str(s1_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
    except Exception as e:
        rows.append([str(rel_folder), s1_path.name, "", "", "", f"ffprobe_failed: {e}"])
        continue

    video_streams = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]

    if not video_streams:
        rows.append([str(rel_folder), s1_path.name, "", "", "", "no_video_stream"])
        continue

    v = video_streams[0]
    r_frame_rate = v.get("r_frame_rate", "")
    avg_frame_rate = v.get("avg_frame_rate", "")
    duration = v.get("duration") or data.get("format", {}).get("duration", "")

    rows.append([
        str(rel_folder),
        s1_path.name,
        r_frame_rate,
        avg_frame_rate,
        duration,
        "",
    ])

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "folder",
        "s1_file",
        "r_frame_rate",
        "avg_frame_rate",
        "duration_s",
        "note",
    ])
    writer.writerows(rows)

print(f"Saved to: {out_csv}")
