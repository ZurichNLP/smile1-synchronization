# SMILE1 S1–GoPro Synchronization

This repository contains scripts developed for the SMILE1 visuoacoustic sign language recognition programming project.

The current pipeline focuses on synchronizing Kinect/S1 recordings with GoPro/S5 recordings, transferring gloss annotations from the Kinect timeline to the GoPro timeline, and generating subtitle files for visual inspection.

## Pipeline overview

The current workflow includes:

- computing Kinect/S1 ↔ GoPro/S5 temporal offsets from `StartMS.txt` and `StartMS2.txt`
- checking S1 video fps and duration
- validating `.ilex` annotation spans against S1 video durations
- merging split GoPro recordings into continuous videos
- transferring `.ilex` gloss annotations from the Kinect timeline to the GoPro timeline
- checking alignment consistency
- generating `.srt` subtitle files for visual inspection together with the GoPro videos

## Scripts

- `scripts/compute_kinect_gopro1_offsets.py`  
  Computes the temporal offset between the Kinect (S1) and GoPro (S5) recordings using `StartMS.txt` and `StartMS2.txt`.

- `scripts/check_s1_fps.py`  
  Checks the frame rate and duration of S1 videos to ensure consistent timing assumptions.

- `scripts/compute_ilex_spans.py`  
  Converts `.ilex` annotation time spans into seconds and computes their overall duration.

- `scripts/compare_s1_and_ilex.py`  
  Compares S1 video durations with the corresponding `.ilex` annotation spans to verify consistency.

- `scripts/merge_all_s5.sh`  
  Merges split GoPro recordings (`S5_*.MP4`) into a single continuous `merged_S5.mp4` file per recording.

- `scripts/final_gloss_to_gopro_alignment.py`  
  Transfers gloss annotations from the Kinect/S1 timeline to the merged GoPro timeline using the computed offsets.

- `scripts/check_alignment.py`  
  Performs sanity checks on the aligned gloss intervals (e.g., invalid ranges or out-of-bound timestamps).

- `scripts/make_srt_from_alignment.py`  
  Generates `.srt` subtitle files from the aligned gloss annotations for visual inspection together with the GoPro videos.

## Notes

Some `.ilex` annotations contain frame values (`FF`) larger than expected for 30 fps videos.  
To avoid invalid intervals caused by unreliable frame-level conversion, the current alignment uses second-level timing instead of frame-level timing.

The scripts are designed as independent processing steps and can be run sequentially as a complete synchronization and alignment pipeline.
