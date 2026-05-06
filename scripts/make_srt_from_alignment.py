import pandas as pd
from pathlib import Path
import re

root = Path("/Users/eldena/Desktop/UZH/2026_Spring/sarah/smile1_data")
csv_path = "/Users/eldena/Desktop/UZH/2026_Spring/sarah/final_gopro_gloss_alignment_ss.csv"
out_dir = root / "srt_outputs"
out_dir.mkdir(exist_ok=True)

df = pd.read_csv(csv_path)

def srt_time(seconds: float) -> str:
    seconds = max(0, float(seconds))
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def safe_name(folder: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", folder)

# keep intervals that at least overlap with GoPro timeline
df = df[
    ~df["status"].astype(str).str.contains("end_before_gopro|start_after_gopro", na=False)
].copy()

# SRT cannot display zero-duration subtitles well
min_duration = 0.5

for folder, sub in df.groupby("folder"):
    sub = sub.sort_values(["gopro_from_start_s", "gopro_from_start_e", "tier", "gloss"])

    out_path = out_dir / f"{safe_name(folder)}_glosses.srt"

    lines = []
    idx = 1

    for _, row in sub.iterrows():
        start = max(0.0, float(row["gopro_from_start_s"]))
        end = float(row["gopro_from_start_e"])

        if end <= start:
            end = start + min_duration

        text = f"{row['tier']}: {row['gloss']}"

        lines.append(str(idx))
        lines.append(f"{srt_time(start)} --> {srt_time(end)}")
        lines.append(text)
        lines.append("")

        idx += 1

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] {folder}: {idx-1} subtitles -> {out_path}")

print(f"\nSaved SRT files to: {out_dir}")
