#!/usr/bin/env python3
"""Create a lightweight AI short drama production pack."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create AI short drama project templates.")
    parser.add_argument("title", help="Project title")
    parser.add_argument("--episodes", type=int, default=8, help="Episode count")
    parser.add_argument("--out", default=".", help="Output directory")
    args = parser.parse_args()

    slug = "".join(ch if ch.isalnum() else "-" for ch in args.title.strip()).strip("-").lower()
    root = Path(args.out) / (slug or "ai-short-drama-project")
    root.mkdir(parents=True, exist_ok=True)

    write_text(
        root / "00-project-brief.md",
        f"""# {args.title}

## One-Liner

## Audience and Platform

## Genre Promise

## First 3-Second Hook

## Production Scope

- Episodes: {args.episodes}
- Duration: 60-90 seconds each
- Format: vertical 9:16
- Style: realistic live-action AI short drama

## Risks

- Character identity drift
- Overacting or unnatural expression
- Voice/subtitle mismatch
- Copyright and platform compliance
""",
    )

    write_csv(
        root / "01-characters.csv",
        [
            "character_id",
            "name",
            "role",
            "age_range",
            "face_identity",
            "hair",
            "wardrobe_signature",
            "personality_baseline",
            "emotional_range",
            "forbidden_changes",
            "reference_images_needed",
        ],
        [],
    )

    rows = [[str(i), "", "", "", "", ""] for i in range(1, args.episodes + 1)]
    write_csv(
        root / "02-episode-beats.csv",
        ["episode", "opening_hook", "pressure", "reveal", "reversal", "cliffhanger"],
        rows,
    )

    write_csv(
        root / "03-shot-list.csv",
        [
            "episode",
            "shot",
            "duration",
            "characters",
            "shot_type",
            "action",
            "micro_expression",
            "image_prompt",
            "video_prompt",
            "audio_subtitle",
        ],
        [],
    )

    write_csv(
        root / "04-voice-subtitles.csv",
        ["line_id", "character", "dialogue_or_voiceover", "emotion", "delivery", "subtitle_text", "sfx_bgm"],
        [],
    )

    write_text(
        root / "05-qa-checklist.md",
        """# QA Checklist

- [ ] First 3 seconds contain conflict or curiosity.
- [ ] Character faces stay consistent.
- [ ] Hair and wardrobe continuity hold.
- [ ] Expressions are readable but restrained.
- [ ] Hands and props are acceptable in key shots.
- [ ] Voice matches character profile.
- [ ] Subtitles match final audio.
- [ ] Music does not bury dialogue.
- [ ] Episode ends with a cliffhanger or reversal.
- [ ] Copyright and platform risks reviewed.
""",
    )

    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
