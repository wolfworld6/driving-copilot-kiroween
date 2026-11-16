#!/usr/bin/env python3
"""Frame sampler for the driving-copilot MVP (spec step 2).

Extracts frames from a dashcam clip at a fixed interval, e.g.:

    python sample_frames.py --input dashcam-urban-cc0.mp4 --interval 5 --outdir frames

Output: frame_001.jpg ... frame_NNN.jpg, one per sampled moment,
t = (N - 1) * interval seconds. Requires ffmpeg on PATH.
"""
import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Extract frames at a fixed interval.")
    p.add_argument("--input", required=True, help="Input video file")
    p.add_argument("--interval", type=float, default=5, help="Seconds between frames (default 5)")
    p.add_argument("--outdir", default="frames", help="Output directory (default frames)")
    p.add_argument("--quality", default="3", help="JPEG quality 2-5, lower is better (default 3)")
    args = p.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"input not found: {src}", file=sys.stderr)
        return 1
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-v", "error",
        "-i", str(src),
        "-vf", f"fps=1/{args.interval}",
        "-q:v", args.quality,
        str(outdir / "frame_%03d.jpg"),
        "-y",
    ]
    subprocess.run(cmd, check=True)
    frames = sorted(outdir.glob("frame_*.jpg"))
    print(f"{len(frames)} frames at {args.interval}s interval -> {outdir}/")
    for i, f in enumerate(frames):
        print(f"  t={(i * args.interval):.0f}s  {f.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
