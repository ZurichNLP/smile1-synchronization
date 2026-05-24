# SMILE1 S5 Segmentation Pipeline

## Goal

Run automatic sign segmentation on the SMILE1 GoPro/S5 data so that the previously computed GoPro-aligned gloss offsets can later be snapped to predicted sign beginnings and endings.

## Input Data

The processed inputs are the merged S5 GoPro recordings from:

```text
/shares/iict-sp2.ebling.cl.uzh/visuoacoustic_slr/glossed/continuous/SMILE1_SRT_participants
```

The batch manifest is:

```text
manifests/smile1_merged_s5_manifest.tsv
```

It contains 9 merged S5 recordings:

```text
203
224
424
813
965
219_1
219_2
966_1
966_2
```

## Tools

- Pose extraction: https://github.com/sign-language-processing/pose
- Segmentation: https://github.com/sign-language-processing/segmentation

The segmentation model expects `.pose` input. The video file is linked in the output ELAN file for inspection, but the model inference itself runs on pose data.

## Final Processing Pipeline

```text
original merged_S5.mp4
-> clean 720p/25fps mp4
-> MediaPipe .pose
-> segmentation .eaf
```

The Slurm array script is:

```text
scripts/run_smile1_s5_segmentation_array.sbatch
```

## Issue Encountered

Directly running `video_to_pose` on the original GoPro files caused PyAV/simple-video-utils video-reading errors on the cluster:

```text
av.error.BlockingIOError: [Errno 11] Resource temporarily unavailable
RuntimeError: Failed to open video
```

The robust solution was to first convert every `merged_S5.mp4` to a clean 720p/25fps MP4 and then generate `.pose` files from those clean videos.

## QC

QC compares each clean video's frame count with the generated pose frame count. The final batch had:

```text
frame_diff = 0
```

for all 9 samples.

Summary files:

```text
results/qc_summary.tsv
results/seg_counts.tsv
```

## Cluster Output Location

Full outputs are stored on the cluster:

```text
/home/xitang/smile1_pose_test/outputs
```

Important subdirectories:

```text
outputs/videos   clean 720p/25fps MP4 files
outputs/poses    generated .pose files
outputs/eaf      segmentation ELAN files
outputs/qc       per-sample QC files
outputs/logs     Slurm logs
```

The repository tracks scripts and small summary outputs, but not large `.mp4` or `.pose` files.
