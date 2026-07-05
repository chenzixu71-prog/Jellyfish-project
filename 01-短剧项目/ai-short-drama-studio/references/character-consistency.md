# Character Consistency Guide

Use before creating any character image, scene image, or image-to-video prompt.

## Identity Lock

Each recurring character needs a stable identity lock:
- character id: short stable code, e.g. FL01, ML01, VIL01
- age range: narrow, e.g. 26-28, not "young"
- face shape
- eye shape and gaze quality
- nose and mouth traits
- skin texture and complexion
- hair style, hairline, hair length, hair color
- body type and height impression
- wardrobe signature
- accessory signature if any
- makeup level
- personality baseline
- emotional range
- forbidden changes
- reference image slots

## Prompt Pattern

Use two layers:

Identity layer:
`[CHAR_ID], same person as reference, Chinese live-action drama actor, age [range], [face shape], [eye traits], [nose/mouth traits], [hair], [skin texture], [body/height impression], [wardrobe signature], realistic natural skin, restrained performance`

Scene layer:
`[location], [shot type], [lighting], [micro-expression], [body action], [relationship tension], [camera/lens], vertical 9:16`

Negative layer:
`different person, changed face, changed hairstyle, changed outfit identity, exaggerated expression, cartoon acting, plastic skin, beauty filter, doll-like face, deformed hands, extra fingers, warped eyes, inconsistent age, heavy makeup unless specified`

## Reference Strategy

Generate in this order:
1. clean portrait front view
2. three-quarter view
3. medium shot in wardrobe
4. full body wardrobe reference
5. neutral expression sheet
6. micro-expression sheet
7. scene keyframes

Do not move to video until the user accepts the character reference sheet.

## Continuity Rules

- Keep hairstyle and wardrobe stable within one scene unless the script explicitly changes time or status.
- Keep makeup intensity stable within a scene.
- Keep scars, accessories, glasses, rings, badges, and uniforms consistent.
- If a character has a disguise, create a separate identity state with a state id, e.g. FL01-disguise.
- Keep lighting and camera language stable for dialogue pairs.

## Image-to-Video Rules

- Use accepted stills as first frames.
- One clip should include one motion and one emotional beat.
- Avoid asking for a full acting scene in one generation.
- Write small actions: "eyes lower for half a second", "breath catches", "jaw tightens", "turns slightly toward the door".
- Keep identity instruction in every video prompt.

## Acceptance Checklist

Before generating many shots, verify:
- same face across 3 angles
- same age impression
- same hairstyle
- same wardrobe logic
- natural skin texture
- usable hands in key shots
- expression range fits character
- no overacting
- no beauty-filter drift
