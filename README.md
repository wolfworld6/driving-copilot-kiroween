# Driving Safety Co-pilot — Kiroween 2026 (Frankenstein)

A talking driving safety co-pilot: dashcam video in, a vision-language model
reads the road, voice gives spoken driving advice.

Track: **Frankenstein** (mash-up tech into one app). Built with Kiro's agent +
spec workflow for Kiroween 2026.

## The idea

Stitch together three things that don't normally belong together — an old
dashcam video feed + a vision-language model + voice interaction — into a
co-pilot that reads the road in real time and talks back with driving advice.

Why this builder: the maintainer of
[AIcity2024-track3](https://github.com/wolfworld6/AIcity2024-track3), the
1st-place solution of the 8th NVIDIA AI City Challenge (2024), Track 3 —
naturalistic driving behavior recognition. This project is that background,
productised.

## What it does today

Pipeline: dashcam clip → frame sampler (5 s interval) → per-frame scene
summary → risk rules → spoken warning/status + transcript log.

| Clip | Content | Result |
|---|---|---|
| 1 — urban drive, 120 s | Calm city drive, pedestrians stay on the sidewalk | 0 warnings, 2 calm status lines (t=40 s, t=85 s), 3 silent watch notes |
| 2 — highway slip road, ~44 s | Van cuts in, then brake-checks (80 → 27 km/h) | 2 warnings: cut-in at t=10 s, sudden braking at t=35 s |

False-alarm check: the calm highway tail of clip 1 (95–115 s) runs through
the same rules and produces 0 warnings.

Rules (`copilot/risk_rules.py`):

- **Warning** (spoken, urgent): pedestrian entering the road, a vehicle
  cutting into our lane, sudden braking ahead. Same-type warnings within
  10 s merge into one spoken warning so the driver is not spammed.
- **Watch** (logged, silent): crossing vehicle, pedestrian on the sidewalk
  near a crossing, oncoming vehicle approaching while we turn. Glare, a red
  light for cross traffic, and cars on the opposite carriageway are
  explicitly not risks.
- **Status** (spoken, at most one per minute, only when no warning fired):
  one calm line at the most notable moment of the minute, otherwise silence.

Current status: the per-frame scene summaries are a first pass produced by
viewing the sampled frames; the VLM API backend that replaces them is the
next engineering step. The risk rules, transcript format and voice pipeline
are final and clip-agnostic.

## How to run the demo

Prerequisites: Python 3, `ffmpeg`.

```bash
# 1. Fetch the clips (not committed: too large, and clip 2 is not
#    openly licensed — see Credits below)
# Clip 1 (CC0): https://commons.wikimedia.org/wiki/File:Dashcam_Recording_(urban).ogv
# Clip 2 (YouTube): https://www.youtube.com/watch?v=LrRt4DSpfKw

# 2. Sample frames every 5 seconds
python copilot/sample_frames.py --input dashcam-urban-cc0.mp4 --interval 5 --outdir frames

# 3. Apply the risk rules (reads a scene_summaries.json)
python copilot/risk_rules.py --summaries copilot/scene_summaries.json --out transcript.json

# 4. Build the demo video (clips + spoken lines mixed in + subtitles)
python demo/build_demo_video.py
```

## Repo layout

- `README.md` — this file.
- `.kiro/steering/product.md` — product steering: the idea, why it fits,
  hard constraints.
- `.kiro/specs/driving-copilot/requirements.md` — MVP spec: recorded clip
  in → scene understanding → spoken warning + transcript, with acceptance
  criteria and the 5-step build order.
- `copilot/sample_frames.py` — fixed-interval frame sampler (ffmpeg).
- `copilot/risk_rules.py` — warning / watch / status rules.
- `copilot/scene_summaries.json` — clip 1 scene summaries (24 moments).
- `copilot/scene_summaries_cutin.json` — clip 2 scene summaries (9 moments).
- `copilot/transcript.json` / `copilot/transcript_cutin.json` — machine-readable
  records of the spoken lines (time, kind, text, audio file).
- `copilot/transcript.md` / `copilot/transcript_cutin.md` — human-readable
  versions of the same records.
- `copilot/audio/` — the four synthesised voice lines referenced by the
  transcripts.
- `demo/build_demo_video.py` — builds the demo video: title card, both
  clips with the spoken lines mixed in at their timestamps and burned-in
  subtitles, end card.

## Credits

- Clip 1: Wikimedia Commons, “Dashcam Recording (urban)”, CC0 public domain.
- Clip 2: YouTube, “Van Cuts In And Dangerously Brake Check Road Rage”,
  Dash Cam Network / Driving MeCrazy (2015). Not openly licensed — used with
  credit, demo audio muted, our own voice-over only.
- Voice-over: synthesised Chinese speech (default system voice).

## Submission rules (Devpost)

- Public GitHub repo with a `/.kiro` directory at the root — required for
  all submissions.
- Work submission deadline: 2026-12-04 14:00 PT (Beijing 12-05 06:00).

## Safety

The co-pilot warns; it never takes control. Short spoken prompts, no screen
staring.
