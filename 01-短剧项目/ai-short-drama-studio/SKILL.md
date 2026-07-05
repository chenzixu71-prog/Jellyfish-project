---
name: ai-short-drama-studio
description: Create AI short drama production packages for Chinese short-video platforms. Use when the user wants help with AI短剧/微短剧 ideation, Douyin/Xiaohongshu research synthesis, scripts, character bibles, consistent live-action character assets, subtle facial expression prompts, text-to-image prompts, image-to-video prompts, voice/TTS, subtitles, editing QA, and Hongguo/Douyin/Kuaishou-style delivery preparation.
---

# AI Short Drama Studio

Use this skill to turn an AI short drama idea into production-ready materials: market notes, premise, character bible, episode outline, scene script, shot list, image prompts, image-to-video prompts, voice/subtitle table, and platform QA.

Prioritize the user's two requirements:

- Keep character identity consistent before and after character modeling.
- Build realistic, live-action character expression assets with rich but restrained micro-expressions. Avoid exaggerated cartoon acting unless requested.

## Workflow

1. Frame the project.
   - Clarify target platform, genre, episode count, episode duration, audience, monetization path, and risk tolerance.
   - If absent, default to a low-cost pilot: 8 episodes, 60-90 seconds each, vertical 9:16, live-action realistic style.

2. Research platform signals.
   - For public web research and platform sample extraction, read `references/social-platform-research.md`.
   - If the user offers Douyin/Xiaohongshu login, ask them to log in themselves in the browser. Do not request or store passwords. Only inspect the minimum pages needed.
   - Record evidence as sample observations, not universal platform truth.

3. Build the drama package.
   - Use `references/drama-production-workflow.md` for the full production pipeline.
   - Produce these deliverables in order: premise, audience hook, genre promise, character bible, relationship map, season arc, episode beats, scripts, shot list, asset list, generation prompts, edit plan, QA checklist.

4. Lock character consistency before generation.
   - Read `references/character-consistency.md` before writing image or video prompts.
   - Create a stable character bible for each recurring role. Include immutable facial identity, body type, hair, wardrobe rules, expression range, forbidden changes, reference image slots, and continuity notes.
   - Never let scene prompts casually rewrite age, face shape, hairstyle, clothing identity, or body proportions.

5. Generate subtle expression prompts.
   - Read `references/micro-expression-library.md` when the user needs character asset sheets, expression variants, acting direction, or shot prompts.
   - Keep expression intensity in the 1-3 range by default. Use natural facial muscle changes, eye focus, breathing, mouth tension, and posture instead of dramatic grimacing.

6. Prepare image and video prompts.
   - Use a two-layer prompt: identity lock + scene instruction.
   - For image-to-video, prefer fixed first frame/reference image, short clip duration, one action per clip, one emotional beat per clip, and explicit continuity constraints.
   - Add negative prompts for identity drift, exaggerated emotion, plastic skin, over-beautification, deformed hands, extra fingers, and changing wardrobe.

7. Prepare voice, subtitles, and edit QA.
   - Use `references/platform-delivery-qa.md` for voice/subtitle/edit checks.
   - Assign each character a voice profile, speaking rhythm, emotional floor/ceiling, and forbidden tone.
   - Build subtitles from final script, then verify against audio after TTS or dubbing.

8. Create structured project files when useful.
   - Run `scripts/create_project_pack.py` to scaffold a production pack from a title and episode count.
   - Use the templates in `references/templates.md` for manual outputs.

## Output Rules

- Separate confirmed evidence, platform sample observations, and creative recommendations.
- Do not claim platform trends from one or two notes. Label small samples as weak signals.
- For Douyin/Xiaohongshu logged-in research, avoid private messages, profile edits, publishing, purchases, downloads of private content, or scraping at scale.
- For platform upload guidance, treat compliance and copyright as product-risk notes, not legal advice.

## Useful Resources

- `references/social-platform-research.md`: Douyin/Xiaohongshu research method and fields.
- `references/live-research-notes.md`: dated logged-in platform research notes and sample table.
- `references/drama-production-workflow.md`: AI short drama pipeline from topic to delivery.
- `references/character-consistency.md`: identity lock, reference image strategy, continuity rules.
- `references/micro-expression-library.md`: restrained live-action micro-expression prompt bank.
- `references/templates.md`: reusable tables and package templates.
- `references/platform-delivery-qa.md`: voice, subtitles, edit, platform delivery checks.
- `scripts/create_project_pack.py`: create a folder of Markdown/CSV templates for a new drama project.
