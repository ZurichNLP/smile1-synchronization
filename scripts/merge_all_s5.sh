#!/bin/bash

ROOT="/shares/iict-sp2.ebling.cl.uzh/visuoacoustic_slr/glossed/continuous/SMILE1_SRT_participants"

echo "Starting batch merge of S5 videos..."

find "$ROOT" -type d | while read dir; do
    cd "$dir" || continue

    files=$(ls *S5*.MP4 *S5*.mp4 2>/dev/null | sort)

    if [ -z "$files" ]; then
        continue
    fi

    echo "[INFO] Processing $dir"

    rm -f list.txt merged_S5.mp4

    for f in $files; do
        echo "file '$f'" >> list.txt
    done

    ffmpeg -nostdin -f concat -safe 0 -i list.txt -c copy merged_S5.mp4 -y

    echo "[DONE] $dir"
done

echo "All merges completed."
