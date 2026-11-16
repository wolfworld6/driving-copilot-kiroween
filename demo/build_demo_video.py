#!/usr/bin/env python3
"""Build the driving-copilot demo video (spec step 5).

Stitches together:
  - title card (3 s)
  - clip 1: urban drive, 120 s, status voice lines at 40 s and 85 s
  - clip 2: highway slip road, 44 s of driving footage, warning voice
    lines at 10 s (cut-in) and 35 s (sudden braking)
  - end card (3 s)

Original clip audio is muted (clip 2's original audio contains strong
language); only our synthesised voice lines are mixed in, at their
timestamps, with the spoken line burned in as a subtitle.

Usage:
    python build_demo_video.py --clips-dir ../hidden_files/clips \
        --out driving-copilot-demo.mp4

Requires ffmpeg with the subtitles and drawtext filters and a CJK font
(Noto Sans CJK SC).
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

W, H = 1280, 720
FONT = "Noto Sans CJK SC"
CARD_BG = "0x111827"

TITLE_LINES = [
    ("驾驶安全副驾", 64, 300, "white"),
    ("Driving Safety Co-pilot", 34, 390, "0x9CA3AF"),
    ("Kiroween 2026 · Frankenstein", 30, 450, "0x9CA3AF"),
]
END_LINES = [
    ("github.com/wolfworld6/driving-copilot-kiroween", 32, 320, "white"),
    ("Kiroween 2026 · 驾驶安全副驾", 28, 380, "0x9CA3AF"),
]

# (start, end, text) — subtitles for the spoken lines, per segment.
SEG1_LINES = [
    (39.5, 47.5, "前方路口有车横穿，右侧人行道有行人，注意观察"),
    (84.5, 91.0, "前方路口，右侧人行道有行人，减速慢行"),
]
SEG2_LINES = [
    (9.5, 13.5, "注意，右侧车辆加塞，保持车距"),
    (34.5, 38.5, "注意，前方车辆急刹，保持车距"),
]
SEG1_LABEL = "片段 1 · 市区行驶（CC0）"
SEG2_LABEL = "片段 2 · 高速匝道（加塞 + 急刹）"


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(path: Path, events) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for i, (start, end, text) in enumerate(events, 1):
            f.write(f"{i}\n{srt_time(start)} --> {srt_time(end)}\n{text}\n\n")


def run(cmd, **kw):
    print(" +", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True, **kw)


def card(out: Path, lines, dur: int = 3) -> None:
    draws = []
    for text, size, y, color in lines:
        draws.append(
            f"drawtext=font='{FONT}':text='{text}':fontsize={size}:"
            f"fontcolor={color}:x=(w-text_w)/2:y={y}"
        )
    # Cards carry a silent audio track so the final concat (which expects
    # audio on every input) does not fail on a missing stream.
    run([
        "ffmpeg", "-v", "error", "-y",
        "-f", "lavfi", "-i", f"color=c={CARD_BG}:s={W}x{H}:d={dur}:r=30",
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-vf", ",".join(draws),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        "-t", str(dur), str(out),
    ])


def segment(out: Path, clip: Path, dur: float, label_srt: Path, lines_srt: Path,
            audios: list[tuple[Path, int]]) -> None:
    """One clip segment: scaled video + label + spoken-line subtitles +
    voice lines mixed over silence. audios = [(file, delay_ms)]."""
    inputs = ["ffmpeg", "-v", "error", "-y", "-i", str(clip)]
    for audio, _ in audios:
        inputs += ["-i", str(audio)]
    style_label = ("force_style='FontName=Noto Sans CJK SC,FontSize=20,"
                   "PrimaryColour=&HCCCCCC,OutlineColour=&H000000,BorderStyle=1,"
                   "Outline=1,Alignment=1,MarginV=20,MarginL=20'")
    style_lines = ("force_style='FontName=Noto Sans CJK SC,FontSize=28,"
                   "PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=1,"
                   "Outline=2,Alignment=2,MarginV=40'")
    vf = (f"scale={W}:{H},fps=30,"
          f"subtitles={label_srt}:{style_label},"
          f"subtitles={lines_srt}:{style_lines}")
    af_parts = [f"anullsrc=r=48000:cl=stereo,atrim=0:{dur}[a0]"]
    amix_inputs = ["[a0]"]
    for i, (audio, delay) in enumerate(audios, 1):
        af_parts.append(
            f"[{i}:a]aresample=48000,adelay={delay}:all=1[a{i}]")
        amix_inputs.append(f"[a{i}]")
    af = ";".join(af_parts) + ";" + "".join(amix_inputs) + \
        f"amix=inputs={len(amix_inputs)}:duration=first:dropout_transition=0[aout]"
    run(inputs + [
        "-filter_complex", f"[0:v]{vf}[v];{af}",
        "-map", "[v]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        "-t", str(dur), str(out),
    ])


def main() -> int:
    p = argparse.ArgumentParser(description="Build the demo video.")
    p.add_argument("--clips-dir", required=True,
                   help="Directory with the clips and audio/ subdir")
    p.add_argument("--out", default="driving-copilot-demo.mp4")
    args = p.parse_args()
    clips = Path(args.clips_dir)
    audio = clips / "audio"
    for name in ("dashcam-urban-cc0.mp4", "cutin-van.mp4"):
        if not (clips / name).exists():
            print(f"missing clip: {clips / name}", file=sys.stderr)
            return 1
    for name in ("status_t040.mp3", "status_t085.mp3",
                 "warning_t010.mp3", "warning_t035.mp3"):
        if not (audio / name).exists():
            print(f"missing audio: {audio / name}", file=sys.stderr)
            return 1

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        label1, lines1 = tmp / "label1.srt", tmp / "lines1.srt"
        label2, lines2 = tmp / "label2.srt", tmp / "lines2.srt"
        write_srt(label1, [(0, 120.05, SEG1_LABEL)])
        write_srt(lines1, SEG1_LINES)
        write_srt(label2, [(0, 44, SEG2_LABEL)])
        write_srt(lines2, SEG2_LINES)
        title, seg1 = tmp / "title.mp4", tmp / "seg1.mp4"
        seg2, end = tmp / "seg2.mp4", tmp / "end.mp4"
        card(title, TITLE_LINES)
        segment(seg1, clips / "dashcam-urban-cc0.mp4", 120.05,
                label1, lines1,
                [(audio / "status_t040.mp3", 40000),
                 (audio / "status_t085.mp3", 85000)])
        segment(seg2, clips / "cutin-van.mp4", 44,
                label2, lines2,
                [(audio / "warning_t010.mp3", 10000),
                 (audio / "warning_t035.mp3", 35000)])
        card(end, END_LINES)
        run([
            "ffmpeg", "-v", "error", "-y",
            "-i", str(title), "-i", str(seg1), "-i", str(seg2), "-i", str(end),
            "-filter_complex",
            "[0:v][0:a][1:v][1:a][2:v][2:a][3:v][3:a]"
            "concat=n=4:v=1:a=1[v][a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            args.out,
        ])
    out = Path(args.out)
    print(f"done: {out} ({out.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
