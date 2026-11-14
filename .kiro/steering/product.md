# Product steering — Driving Safety Co-pilot (Kiroween 2026, Frankenstein)

> Draft prepared 2026-11-14 for the user's approval. Nothing here has been
> pushed anywhere; it becomes the repo's `.kiro/steering/product.md` only
> when the user says to create the public repo.

## The idea (as approved on the credits form, 2026-11-07)

Stitch together three things that don't normally belong together — an old
dashcam video feed + a vision-language model + voice interaction — into a
"talking driving safety co-pilot" that reads the road in real time and
gives spoken driving advice.

Track: **Frankenstein** — mash-up tech into one app. Backup track if this
is re-scoped: Skeleton Crew.

## Why this idea fits the builder

- The user is the maintainer of wolfworld6/AIcity2024-track3, the 1st-place
  solution of the 8th NVIDIA AI City Challenge (2024), Track 3 — naturalistic
  driving behavior recognition. This project is that background, productised.
- The same perception stack (driver / road-scene understanding) is reused;
  the new parts are the VLM reasoning layer and the voice loop.

## Product principles

1. **Safety first, advice second.** The co-pilot warns; it never takes
   control, and it never distracts: short spoken prompts, no screen staring.
2. **Real video in, real advice out.** Demo on real dashcam clips first;
   synthetic footage only as a fallback.
3. **Spec-driven, small MVP.** One working loop beats a broad feature list:
   video in → scene understanding → spoken advice.
4. **Kiro-native.** Built with Kiro's agent + spec workflow (that's the
   point of the hackathon); the `.kiro` specs in this scaffold are the
   starting spec, not decoration.

## Hard constraints (from Devpost rules, confirmed 2026-11-13)

- Submission MUST be a **public GitHub repo with a `/.kiro` directory at
  the root** — missing it invalidates the submission. Build in public
  from the start; do not prototype in a private repo first.
- Work submission deadline: **2026-12-04 14:00 PT (Beijing 12-05 06:00)**.
- 4,000 Kiro Credits: redeem by 2026-12-04 (user clicks the one-time link
  himself); redeemed credits expire 2026-12-31 23:59 PT (Beijing
  2027-01-01 15:59).

## Open decisions (user's call, not assumed)

- Repo name. Suggestion: `driving-copilot-kiroween` under wolfworld6.
  (Do not reuse AIcity2024-track3 — that repo is the Codex application
  project, a different thing.)
- Which dashcam clips to demo on, and whether the VLM runs via API or
  local model.
