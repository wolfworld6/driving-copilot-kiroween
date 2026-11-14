# Spec draft — Driving Safety Co-pilot MVP

> Draft prepared 2026-11-14 for the user's approval. This is the starting
> spec for `.kiro/specs/driving-copilot/`; refine it with the user before
> building.

## Requirements (EARS-style, draft)

1. WHEN a dashcam video clip is loaded, THE SYSTEM SHALL extract frames at
   a fixed interval and produce a scene summary (road type, nearby vehicles,
   pedestrians, traffic signals) for each sampled moment.
2. WHEN the scene contains a risky event (e.g. sudden braking ahead, a
   pedestrian entering the road, lane drift), THE SYSTEM SHALL generate a
   short spoken warning within the clip's playback window.
3. WHEN no risk is detected, THE SYSTEM SHALL stay silent or give at most
   one brief status update per minute — no chatter.
4. THE SYSTEM SHALL present the advice as voice output (text-to-speech);
   a text transcript of each warning SHALL be logged alongside its
   timestamp in the clip.
5. THE SYSTEM SHALL run end-to-end on a recorded clip before any live
   camera work is attempted (recorded-first, live-later).

## Non-goals for the MVP

- No vehicle control, no real-time live camera pipeline, no phone app.
- No multi-language voice in v1 (Chinese first, matching the demo audience).

## Acceptance criteria (demo-ready)

- [ ] A 1–2 minute real dashcam clip plays with spoken warnings at the
      right moments, transcript visible.
- [ ] At least two distinct risk types are caught (e.g. cut-in + pedestrian).
- [ ] False-alarm rate on a calm highway clip is visibly low (no warnings,
      or one status line only).
- [ ] Repo is public, `/.kiro` at root, README explains how to run the demo.

## Suggested build order

1. Repo + `.kiro` skeleton (this scaffold).
2. Frame sampler + VLM scene summary on one clip.
3. Risk rules + spoken warnings + transcript log.
4. Second clip (different risk type) + false-alarm check.
5. README + demo video + Devpost submission.
