#!/bin/bash
#SBATCH --job-name=smile1s5
#SBATCH --output=/home/xitang/smile1_pose_test/outputs/logs/smile1s5_%A_%a.out
#SBATCH --error=/home/xitang/smile1_pose_test/outputs/logs/smile1s5_%A_%a.err
#SBATCH --time=06:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --array=0-8

set -euo pipefail

MANIFEST=/home/xitang/smile1_pose_test/smile1_merged_s5_manifest.tsv
LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$MANIFEST")
ID=$(echo "$LINE" | cut -f1)
INPUT=$(echo "$LINE" | cut -f2)

BASE=/home/xitang/smile1_pose_test/outputs
CLEAN="$BASE/videos/${ID}_merged_S5_720p25_clean.mp4"
POSE="$BASE/poses/${ID}_merged_S5_720p25.pose"
EAF="$BASE/eaf/${ID}_merged_S5_720p25.eaf"
QC="$BASE/qc/${ID}_qc.txt"

echo "ID=$ID"
echo "INPUT=$INPUT"

ffmpeg -y \
  -i "$INPUT" \
  -map 0:v:0 \
  -vf "scale=-2:720,fps=25,format=yuv420p" \
  -an -sn -dn \
  -preset veryfast \
  -movflags +faststart \
  "$CLEAN"

ffprobe -v error \
  -select_streams v:0 \
  -count_frames \
  -show_entries stream=nb_read_frames,avg_frame_rate,duration \
  -of default=nw=1 \
  "$CLEAN" > "$QC"

export PYTHONPATH=/home/xitang/smile1_pose_test/pose_retest
export PATH=/home/xitang/smile1_pose_test/pose_retest/bin:$PATH

video_to_pose --format mediapipe --workers 1 \
  -i "$CLEAN" \
  -o "$POSE"

PYTHONPATH=/home/xitang/smile1_pose_test/pose_retest python3 - "$POSE" "$QC" <<'PY'
from pose_format import Pose
from pathlib import Path
import sys

pose_path = Path(sys.argv[1])
qc_path = Path(sys.argv[2])

with pose_path.open("rb") as f:
    pose = Pose.read(f.read())

with qc_path.open("a") as f:
    f.write(f"pose_fps={pose.body.fps}\n")
    f.write(f"pose_frames={pose.body.data.shape[0]}\n")
    f.write(f"pose_duration={pose.body.data.shape[0] / pose.body.fps}\n")
PY

export CUDA_VISIBLE_DEVICES=""
export PYTHONPATH=/home/xitang/smile1_pose_test/segment_cpu

python3 -m sign_language_segmentation.bin \
  --pose "$POSE" \
  --elan "$EAF" \
  --video "$CLEAN" \
  --device cpu

echo "DONE $ID"
