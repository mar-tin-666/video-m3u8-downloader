# video-m3u8-downloader
- This script downloads and merges video segments from an .m3u8 playlist.
- It fetches all .ts segments, merges them, and saves the final output as an .mp4 file.
- Required ffmpeg - https://www.ffmpeg.org/download.html
- Errors `[h264 @ ...] non-existing PPS 0 referenced` / `[h264 @ ...] decode_slice_header error` / `[h264 @ ...]  no frame!` are ok :)
