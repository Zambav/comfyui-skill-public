# JoyCaption Convention

> Portable convention for using JoyCaption as a vision-to-text step in an
> image-to-prompt pipeline. This document is model/tool agnostic; it does not
> assume a specific JoyCaption build, model filename, or machine layout.

---

## What JoyCaption Is (and Isn't)

**JoyCaption is a vision-to-text tool.** Given an image, it outputs a textual
description of what it sees: objects, lighting, composition, textures, mood,
spatial arrangement.

**JoyCaption does NOT write prompts.** It does not add camera directions,
motion language, cinematic style, or production intent. Those are separate
creative decisions, added by a human or by an LLM in a downstream step.

Treat JoyCaption's output as **raw observational data**, not as a final prompt.

---

## The `joycaption.md` File

### What it is

`joycaption.md` is a structured Markdown document that captures scene
descriptions for a batch of images. It is the **canonical source of truth** for
what each image contains and how it was originally characterized.

When an LLM later generates cinematic prompts, it reads `joycaption.md` and
adds creative direction on top -- it does not modify the descriptions.

### Naming variants (check all)

JoyCaption files may be named any of the following. Check all three before
assuming none exists:

```
INPUT_FOLDER/joycaption.md
INPUT_FOLDER/joycaption_{foldername}.md
INPUT_FOLDER/joycaption_{asset_name}.md
```

Example for an input folder named `Render Dump`:

- `Render Dump/joycaption.md`
- `Render Dump/joycaption_render_dump.md`
- `Render Dump/joycaption_mandalorian_scene.md`

### Format

One section per image, in Markdown:

```markdown
## filename.jpg

A wide establishing shot of an alien canyon at golden hour. Rust-red rock
formations tower on both sides, casting long shadows across the sandy canyon
floor. A small figure stands near the left edge for scale. Dust motes catch the
warm low-angle light. Hazy atmosphere fades to pale orange at the horizon.
```

Rules:

- Heading is `## filename.ext` (exact filename, no path)
- One descriptive paragraph per image
- No camera direction, no motion, no "the camera could..."
- Descriptions are observational, not prescriptive

---

## When to Check for `joycaption.md`

**Before doing anything involving prompts for a given image set, check for
`joycaption.md` first.**

Locations to check in order:

1. `{INPUT_FOLDER}/joycaption.md`
2. `{INPUT_FOLDER}/{folder_name}_joycaption.md`
3. The current job's output folder, if a job was already started

If found, ask the user:

> "I found an existing `joycaption.md` for this folder. Would you like to
> use it as-is, update it, or start fresh?"

Do not regenerate without asking -- the existing file represents decisions
already made.

---

## When to Create `joycaption.md`

Create it when:

- A new image set has no descriptions yet
- The user explicitly asks to run JoyCaption
- No `joycaption.md` exists in the input folder

**How to run JoyCaption** (build-specific, see your tool's docs):

```bash
# Example for llama.cpp's mtmd CLI. Substitute your own binary and flags.
llama-mtmd-cli \
  --model /path/to/joycaption/model.gguf \
  --mmproj /path/to/joycaption/mmproj.gguf \
  --image path/to/image.jpg \
  --prompt "Write a long, detailed caption." \
  > captions.txt
```

The raw output goes to `captions.txt` in the same folder. Then organize those
descriptions into `joycaption.md` format with `## filename.jpg` headings.

---

## Description Rules

- Describe what is *in* the image, not what could be done with it
- Include: lighting quality and direction, dominant colors, spatial scale,
  subject position, texture notes, atmospheric conditions
- Do NOT include: camera movement suggestions, editing instructions,
  production intent
- Write in third person, observational tone
- One paragraph per image -- enough to reconstruct the visual scene

---

## How `joycaption.md` Feeds Into Prompt Generation

The pipeline:

```
joycaption.md descriptions
        |
        v
LLM reads each ## filename section
        |
        v
LLM writes a UNIQUE cinematic prompt per image
(varied camera language, motion, mood -- NOT just scene description)
        |
        v
Prompts saved to {job_folder}/{model}_prompts.json
        |
        v
batch runner loads JSON -> ComfyUI
```

The LLM layer adds the cinematic direction (camera moves, lighting mood,
motion intent) on top of what JoyCaption observed. The `joycaption.md`
descriptions are never modified after generation.

---

## Prompt Versioning

When re-generating prompts for the same image set (new cinematic direction):

- Add a new top-level `_version` block in the JSON:
  `{v: 2, description, date, negative}`
- Never overwrite v1
- Keep old JSONs -- they document what was used for each render iteration

Example prompt JSON:

```json
{
  "_version": {
    "v": 1,
    "description": "Initial cinematic pass -- outdoor scenes, warm lighting",
    "date": "2026-04-01",
    "negative": "avoid locked-off static frame as sole camera behaviour, frozen motion, still photography, cartoonish"
  },
  "image_001.jpg": {
    "prompt": "The camera slowly tracks right as the subject walks forward...",
    "description": "Person walking on cobblestone street at golden hour"
  }
}
```

---

## Negative Prompt Standard

Use sparingly and specifically:

```
"avoid locked-off static frame as sole camera behaviour, frozen motion, still photography, cartoonish"
```

Let the positive prompt describe what *should* happen. The model responds
better to direction than negation. Do not pile on synonyms
("static, still, frozen, motionless, no movement") -- one concise negative
phrase is enough.

---

*This document is portable. Adapt the `llama-mtmd-cli` invocation to whatever
vision-to-text tool your stack uses (JoyCaption, LLaVA, CogVLM, Florence-2, etc.).
The naming convention and pipeline rules stay the same.*
