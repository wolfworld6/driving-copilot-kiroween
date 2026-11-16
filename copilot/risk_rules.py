#!/usr/bin/env python3
"""Risk rules + spoken warnings for the driving-copilot MVP (spec step 3).

Reads scene_summaries.json (spec step 2 output) and emits a transcript:
- WARNING (spoken, urgent): pedestrian entering the road, cut-in, sudden
  braking ahead. Must fire within the clip's playback window.
- WATCH (logged only, never spoken): crossing vehicle, pedestrian on the
  sidewalk near a crossing, oncoming vehicle approaching while we turn.
- STATUS (spoken, at most ONE per 60 s window when no warning fired):
  one calm line at the most notable moment of the minute, else silence.

Deliberately NOT watch triggers: sun glare alone, a red light for cross
traffic, a car on the opposite carriageway — all normal, not risks.

Usage:
    python risk_rules.py --summaries scene_summaries.json --out transcript.json
"""
import argparse
import json
from pathlib import Path

# --- keyword rules (match against the Chinese summary fields) ---
WARN_PED = ("进入车道", "横穿马路", "在车道上", "闯入车道")
WARN_CUTIN = ("加塞", "突然并入", "切入本车道")
WARN_BRAKE = ("急刹", "紧急制动")


def _has(text: str, keys) -> bool:
    return any(k in (text or "") for k in keys)


def watch_features(m: dict) -> dict:
    """Which watch conditions hold for one sampled moment."""
    veh, ped = m.get("vehicles", ""), m.get("pedestrians", "")
    return {
        # a vehicle crossing our path (not merely present)
        "crossing": _has(veh, ("横穿",)),
        # pedestrian on the sidewalk near the road (not in the road)
        "sidewalk_ped": _has(ped, ("人行道",)),
        # oncoming vehicle actually approaching us, not one on a
        # separated opposite carriageway
        "oncoming": "对向" in veh and _has(veh, ("驶来", "迎面")),
    }


def classify(m: dict) -> str:
    """Return 'warning' | 'watch' | 'none' for one sampled moment."""
    veh, ped = m.get("vehicles", ""), m.get("pedestrians", "")
    if _has(ped, WARN_PED) or _has(veh, WARN_CUTIN) or _has(veh, WARN_BRAKE):
        return "warning"
    if any(watch_features(m).values()):
        return "watch"
    return "none"


def notability(m: dict) -> int:
    """How notable a watch moment is: count of watch features + signals."""
    score = sum(1 for v in watch_features(m).values() if v)
    if m.get("signals", "无") != "无":
        score += 1
    return score


def status_line(m: dict) -> str:
    """Compose one calm status line for a chosen moment (Chinese, spoken)."""
    feats = watch_features(m)
    veh, ped, road = m.get("vehicles", ""), m.get("pedestrians", ""), m.get("road_type", "")
    clauses = []
    if feats["crossing"]:
        clauses.append("前方路口有车横穿")
    elif "路口" in road:
        clauses.append("前方路口")
    if feats["sidewalk_ped"]:
        clauses.append("右侧人行道有行人" if "右侧" in ped else "人行道上有行人")
    if feats["oncoming"]:
        clauses.append("对向有来车")
    if not clauses:
        if "地库" in road or "车库" in road:
            return "地库行驶，路况正常"
        if "快速路" in road or "高速" in road:
            return "快速路行驶，路况正常"
        return "市区行驶，路况正常"
    if feats["crossing"] or feats["oncoming"]:
        return "，".join(clauses) + "，注意观察"
    return "，".join(clauses) + "，减速慢行"


def warning_type(m: dict) -> str:
    """Which warning kind a moment is: pedestrian | cutin | brake."""
    veh, ped = m.get("vehicles", ""), m.get("pedestrians", "")
    if _has(ped, WARN_PED):
        return "pedestrian"
    if _has(veh, WARN_CUTIN):
        return "cutin"
    return "brake"


def warning_line(m: dict) -> str:
    veh, ped = m.get("vehicles", ""), m.get("pedestrians", "")
    if _has(ped, WARN_PED):
        return "注意，行人进入车道，减速停车"
    if _has(veh, WARN_CUTIN):
        side = "右侧" if "右侧" in veh else "左侧"
        return f"注意，{side}车辆加塞，保持车距"
    return "注意，前方车辆急刹，保持车距"


def run(summaries: dict) -> dict:
    moments = summaries["moments"]
    duration = summaries["duration_s"]
    entries = []
    warnings = [m for m in moments if classify(m) == "warning"]

    # Warnings: one spoken warning per event. Same-type warning moments
    # within 10 s are one continuing event (e.g. two cars cutting in
    # back-to-back); they merge into the first warning, and the merged
    # moments are listed on the entry so nothing is hidden.
    groups: list[list[dict]] = []
    for m in warnings:
        if groups and warning_type(m) == warning_type(groups[-1][0]) \
                and m["t"] - groups[-1][-1]["t"] <= 10:
            groups[-1].append(m)
        else:
            groups.append([m])
    for g in groups:
        first = g[0]
        entry = {
            "t": first["t"], "kind": "warning", "spoken": True, "audio": None,
            "text": warning_line(first), "frame": first["frame"],
        }
        if len(g) > 1:
            entry["merged_t"] = [m["t"] for m in g[1:]]
            entry["detail"] = "；".join(f"t={m['t']}s {m['summary']}" for m in g)
        entries.append(entry)

    # Status: at most one spoken line per 60 s window, only in windows
    # without a warning. Pick the most notable watch moment in the window
    # (earliest wins ties); if none, stay silent that minute.
    for start in range(0, int(duration), 60):
        if any(start <= w["t"] < start + 60 for w in warnings):
            continue
        window = [m for m in moments if start <= m["t"] < start + 60]
        watches = [m for m in window if classify(m) == "watch"]
        if not watches:
            continue
        chosen = max(watches, key=lambda m: (notability(m), -m["t"]))
        entries.append({
            "t": chosen["t"], "kind": "status", "spoken": True, "audio": None,
            "text": status_line(chosen), "frame": chosen["frame"],
        })

    # Watch moments not chosen as the minute's status line: logged, silent.
    spoken_ts = {e["t"] for e in entries}
    for m in moments:
        if classify(m) == "watch" and m["t"] not in spoken_ts:
            entries.append({
                "t": m["t"], "kind": "watch", "spoken": False, "audio": None,
                "text": "观察：" + m["summary"], "frame": m["frame"],
            })

    entries.sort(key=lambda e: e["t"])
    return {
        "clip": summaries["clip"],
        "duration_s": duration,
        "rules": "warning=cut-in/pedestrian-in-road/sudden-braking; "
                 "watch=crossing-vehicle/sidewalk-pedestrian/approaching-oncoming; "
                 "status<=1 per 60s window, silent otherwise; "
                 "glare/cross-traffic-red/opposite-carriageway are not risks",
        "counts": {
            "warning": sum(1 for e in entries if e["kind"] == "warning"),
            "status": sum(1 for e in entries if e["kind"] == "status"),
            "watch": sum(1 for e in entries if e["kind"] == "watch"),
        },
        "entries": entries,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Apply risk rules to scene summaries.")
    p.add_argument("--summaries", required=True)
    p.add_argument("--out", default="transcript.json")
    args = p.parse_args()
    summaries = json.loads(Path(args.summaries).read_text(encoding="utf-8"))
    result = run(summaries)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    c = result["counts"]
    print(f"warnings={c['warning']} status={c['status']} watch={c['watch']} -> {args.out}")
    for e in result["entries"]:
        mark = "播报" if e["spoken"] else "静默记录"
        print(f"  t={e['t']:>3}s [{e['kind']:<7}] {mark}: {e['text']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
