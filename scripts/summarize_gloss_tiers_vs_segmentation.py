#!/usr/bin/env python3
"""Summarize iLex gloss-tier counts against segmentation SIGN counts.

The GoPro-aligned gloss alignment uses folder IDs such as `219/1`, whereas the
segmentation outputs use sample IDs such as `219_1`. This script normalizes the
IDs and writes one row per SMILE1 merged S5 sample.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


TIER_COLUMNS = {
    "BH-Glosse": "bh_gloss_rows",
    "RH-Glosse": "rh_gloss_rows",
    "LH-Glosse": "lh_gloss_rows",
}


def normalize_sample_id(folder: str) -> str:
    return folder.replace("/", "_")


def read_manifest(path: Path) -> list[str]:
    samples: list[str] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.reader(f, delimiter="\t"):
            if row:
                samples.append(row[0])
    return samples


def read_seg_counts(path: Path) -> dict[str, dict[str, int]]:
    with path.open(newline="", encoding="utf-8") as f:
        return {
            row["sample"]: {
                "segmentation_sign_segments": int(row["signs"]),
                "segmentation_sentence_segments": int(row["sentences"]),
            }
            for row in csv.DictReader(f, delimiter="\t")
        }


def read_gloss_tier_counts(path: Path) -> dict[str, Counter]:
    counts: dict[str, Counter] = defaultdict(Counter)
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            sample = normalize_sample_id(row["folder"])
            tier = row["tier"]
            if tier in TIER_COLUMNS:
                counts[sample][tier] += 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alignment", required=True, type=Path)
    parser.add_argument("--seg-counts", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    samples = read_manifest(args.manifest)
    seg_counts = read_seg_counts(args.seg_counts)
    gloss_counts = read_gloss_tier_counts(args.alignment)

    fieldnames = [
        "sample",
        "bh_gloss_rows",
        "rh_gloss_rows",
        "lh_gloss_rows",
        "bh_rh_gloss_rows",
        "all_gloss_rows",
        "segmentation_sign_segments",
        "segmentation_sentence_segments",
        "bh_rh_minus_sign_segments",
        "all_gloss_minus_sign_segments",
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for sample in samples:
            tiers = gloss_counts.get(sample, Counter())
            bh = tiers["BH-Glosse"]
            rh = tiers["RH-Glosse"]
            lh = tiers["LH-Glosse"]
            bh_rh = bh + rh
            all_gloss = bh + rh + lh
            signs = seg_counts.get(sample, {}).get("segmentation_sign_segments", 0)
            sentences = seg_counts.get(sample, {}).get("segmentation_sentence_segments", 0)
            writer.writerow(
                {
                    "sample": sample,
                    "bh_gloss_rows": bh,
                    "rh_gloss_rows": rh,
                    "lh_gloss_rows": lh,
                    "bh_rh_gloss_rows": bh_rh,
                    "all_gloss_rows": all_gloss,
                    "segmentation_sign_segments": signs,
                    "segmentation_sentence_segments": sentences,
                    "bh_rh_minus_sign_segments": bh_rh - signs,
                    "all_gloss_minus_sign_segments": all_gloss - signs,
                }
            )

    print(args.output)


if __name__ == "__main__":
    main()
