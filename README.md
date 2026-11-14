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

## How this repo is organised

- `.kiro/steering/product.md` — product steering: the idea, why it fits,
  hard constraints.
- `.kiro/specs/driving-copilot/requirements.md` — MVP spec draft: recorded
  clip in → scene understanding → spoken warning + transcript, with
  acceptance criteria and a 5-step build order.

## MVP build order

1. Repo + `.kiro` skeleton (this scaffold).
2. Frame sampler + VLM scene summary on one clip.
3. Risk rules + spoken warnings + transcript log.
4. Second clip (different risk type) + false-alarm check.
5. README + demo video + Devpost submission.

## Submission rules (Devpost)

- Public GitHub repo with a `/.kiro` directory at the root — required for
  all submissions.
- Work submission deadline: 2026-12-04 14:00 PT (Beijing 12-05 06:00).

## Safety

The co-pilot warns; it never takes control. Short spoken prompts, no screen
staring.
