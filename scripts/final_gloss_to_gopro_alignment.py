
import csv
import re
import xml.etree.ElementTree as ET
from pathlib import Path

root_dir = Path("/Users/eldena/Desktop/UZH/2026_Spring/sarah/smile1_data")
offset_csv = root_dir / "kinect_gopro1_offsets.csv"
duration_csv = Path("/Users/eldena/Desktop/UZH/2026_Spring/sarah/smile1_data/merged_s5_duration_check_final.tsv")
out_csv = root_dir / "final_gopro_gloss_alignment_ss.csv"

FPS = 30

def tc_to_seconds(tc: str) -> float:
    hh, mm, ss, ff = map(int, tc.split(":"))
    return hh * 3600 + mm * 60 + ss

# Load offsets
offsets = {}
with open(offset_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        offsets[row["folder"]] = float(row["offset_s"])

# Load merged GoPro durations
durations = {}
with open(duration_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        durations[row["folder"]] = float(row["merged_duration_s"])

rows_out = []

for ilex_path in root_dir.rglob("*.ilex"):
    folder = str(ilex_path.parent.relative_to(root_dir))

    if folder not in offsets:
        print(f"[SKIP] No offset for {folder}")
        continue

    if folder not in durations:
        print(f"[SKIP] No merged GoPro duration for {folder}")
        continue

    offset_s = offsets[folder]
    merged_duration_s = durations[folder]

    try:
        tree = ET.parse(ilex_path)
        root = tree.getroot()
    except Exception as e:
        print(f"[SKIP] Failed to parse {ilex_path.name}: {e}")
        continue

    # token id -> type id
    token_to_type = {}
    for tok in root.findall("token"):
        tok_id = tok.attrib.get("id")
        type_id = tok.attrib.get("type")
        if tok_id and type_id:
            token_to_type[tok_id] = type_id

    # type id -> gloss name
    type_to_name = {}
    for typ in root.findall("type"):
        type_id = typ.attrib.get("id")
        name = typ.attrib.get("name")
        if type_id and name:
            type_to_name[type_id] = name

    # tier id -> tier name
    tier_id_to_name = {}
    gloss_tier_ids = set()

    for tier in root.findall("tier"):
        tier_id = tier.attrib.get("id")
        tier_name = tier.attrib.get("name")
        if tier_id and tier_name:
            tier_id_to_name[tier_id] = tier_name
            if tier_name in {"RH-Glosse", "BH-Glosse", "LH-Glosse"}:
                gloss_tier_ids.add(tier_id)

    if not gloss_tier_ids:
        print(f"[SKIP] No gloss tiers found in {ilex_path.name}")
        continue

    # Use earliest timecode in the ilex file as S1/Kinect start timecode
    all_starts = []
    for tag in root.findall("tag"):
        tc_start = tag.attrib.get("timecode_start")
        if tc_start:
            all_starts.append(tc_start)

    if not all_starts:
        print(f"[SKIP] No timecodes found in {ilex_path.name}")
        continue

    s1_start_tc = min(all_starts)
    s1_start_seconds = tc_to_seconds(s1_start_tc)

    count = 0

    for tag in root.findall("tag"):
        tier_id = tag.attrib.get("tier")
        if tier_id not in gloss_tier_ids:
            continue

        tc_start = tag.attrib.get("timecode_start")
        tc_end = tag.attrib.get("timecode_end")
        token_dom = tag.attrib.get("token_dom")

        if not tc_start or not tc_end or not token_dom:
            continue

        type_id = token_to_type.get(token_dom)
        gloss = type_to_name.get(type_id, "UNKNOWN")
        tier_name = tier_id_to_name.get(tier_id, "UNKNOWN_TIER")

        kinect_from_start_s = tc_to_seconds(tc_start) - s1_start_seconds
        kinect_from_start_e = tc_to_seconds(tc_end) - s1_start_seconds

        gopro_from_start_s = kinect_from_start_s + offset_s
        gopro_from_start_e = kinect_from_start_e + offset_s

        issues = []

        if kinect_from_start_s >= kinect_from_start_e:
            issues.append("kinect_start>=end")

        if gopro_from_start_s >= gopro_from_start_e:
            issues.append("gopro_start>=end")

        if gopro_from_start_s < 0:
            issues.append("start_before_gopro")

        if gopro_from_start_e < 0:
            issues.append("end_before_gopro")

        if gopro_from_start_s > merged_duration_s:
            issues.append("start_after_gopro")

        if gopro_from_start_e > merged_duration_s:
            issues.append("end_after_gopro")

        if not issues:
            status = "inside_gopro"
        else:
            status = ";".join(issues)

        rows_out.append([
            folder,
            ilex_path.name,
            tier_name,
            gloss,
            tc_start,
            tc_end,
            s1_start_tc,
            round(kinect_from_start_s, 6),
            round(kinect_from_start_e, 6),
            round(offset_s, 6),
            round(gopro_from_start_s, 6),
            round(gopro_from_start_e, 6),
            round(merged_duration_s, 6),
            status,
        ])

        count += 1

    print(f"[OK] {folder}: {count} gloss rows")

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "folder",
        "ilex_file",
        "tier",
        "gloss",
        "tc_start",
        "tc_end",
        "s1_start_tc",
        "kinect_from_start_s",
        "kinect_from_start_e",
        "offset_s",
        "gopro_from_start_s",
        "gopro_from_start_e",
        "merged_gopro_duration_s",
        "status",
    ])
    writer.writerows(rows_out)

print(f"\nSaved to: {out_csv}")
print(f"Total rows: {len(rows_out)}")
