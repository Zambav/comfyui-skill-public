# AGENTS.md — AI Agent Instructions

> How an AI coding/operations agent (Hermes, Claude Code, Codex, etc.) should
> work with this skill in any environment.

This file exists so that an agent dropped into the project cold -- with no
prior context -- can use the skill correctly on first contact. Read this
**before** reading any other file in this skill.

---

## What this skill is

`comfyui-skill-public` is a **portable, installation-agnostic** operating
model for ComfyUI. It contains:

- Prompting guides per model family (FLUX 2, LTX 2.3, WAN 2.2, general)
- Reference implementations of node maps and batch helpers
- A sanitized `scripts/api_lib.py` for talking to a ComfyUI instance
- A convention for JoyCaption-driven image description
- SOPs for batch operations, monitoring, and cron-based recovery

It is **not** tied to any specific:

- Machine path or username
- Discord channel, model filename, or checkpoint
- ComfyUI version (only the version range documented in `dependencies.md`)
- Custom node set (some demo workflows need custom nodes; check before running)

---

## File placement rules

| File type | Correct location | Never at... |
|-----------|------------------|-------------|
| Skill metadata (`SKILL.md`, `README.md`) | repo root | subdirectories |
| Prompting guides | `prompting-guides/` | root or `docs/` |
| Reference implementations | `reference-implementations.md` (root) | `docs/` |
| Setup, dependencies, models | `setup.md`, `dependencies.md`, `models.md` (root) | anywhere else |
| Job/cron SOPs | `batch-operations.md`, `cron-jobs.md` (root) | `docs/` |
| Demo workflow JSONs | `demo-workflows/` (READ ONLY examples) | `workflows/`, project root |
| Shared helper code | `scripts/` (e.g. `api_lib.py`) | project root |
| Cross-cutting conventions | `docs/` (e.g. `joycaption-convention.md`) | repo root |

**Why this matters:** agents scanning a skill expect a stable layout. If
`SKILL.md` is at root and `setup.md` is at root but `reference-implementations.md`
is in `docs/`, the agent wastes context hunting for things that should be
predictable.

---

## Read path for an agent (cold start)

1. **`SKILL.md`** (root) -- decide if this skill applies to the user's request
2. **`setup.md`** (root) -- if ComfyUI install is unknown
3. **`prompting-guides/README.md`** -- pick the model family guide
4. **`reference-implementations.md`** -- node maps and code patterns
5. **`scripts/api_lib.py`** -- production-quality helper to copy or import
6. **`batch-operations.md` + `cron-jobs.md`** -- only if running a batch
7. **`docs/joycaption-convention.md`** -- only if generating prompts from images

When the user gives an install, you can skip step 2 and proceed.

---

## The hard rules

1. **Never edit a base workflow JSON file directly.** Always deep copy, patch,
   and load the copy. This is enforced in the reference `api_lib.py` patterns.
2. **Never assume absolute paths.** All paths come from the user, from
   `/object_info` discovery, or from environment variables. If you find
   yourself about to write a path like `/absolute/path/to/users/dir/...`, stop and ask
   the user.
3. **Never assume a model filename is available.** Always confirm via
   `/object_info` or by listing the relevant model folder on the target install.
4. **Never skip the WebSocket block on `/history` verification.** Fire-and-forget
   queueing is unreliable -- the proven pattern is one WS, one client_id,
   blocking until ComfyUI signals done, then verifying with `/history`.
5. **Never overwrite a `joycaption.md` without asking.** It represents
   decisions already made. If found, surface it to the user.
6. **Never assume a Discord channel ID, Discord bot token, or notification
   destination.** Always ask the user at batch startup, and let the answer
   be parameterized.

---

## What to do when triggered

When the user's request matches a trigger phrase in `SKILL.md` (image gen,
batch edit, video, LoRA training, etc.):

1. **Open `SKILL.md`** to confirm trigger scope and routing.
2. **Open the matching `prompting-guides/*.md`** for prompt style.
3. **Open `reference-implementations.md`** for node map and patch pattern.
4. **Ask the minimum questions** needed (see "Intake questionnaire" below).
5. **Discover the install** with `/object_info` -- confirm node classes,
   dropdown model values, and encoder/VAE availability.
6. **Generate, queue, monitor, verify** using the patterns in `scripts/api_lib.py`
   and the reference implementations.

If the user already provided the install info, you can skip discovery. But
always confirm node classes before submitting a workflow.

---

## Intake questionnaire (image batch tasks)

For an image generation or batch-edit request, ask the user for:

1. **"Where are the photos / what's the input folder?"** (input path)
2. **"Where should outputs go?"** (output path) -- or accept auto-derived
   `{input_folder}/{input_folder_name} flux edit batch/`
3. **"What should I call this batch?"** (short description, becomes the
   job folder name)
4. **"What's the prompt?"** (edit instruction or text description)
5. **"One batch, or multiple batches with different prompts?"**
6. For video (LTX / WAN): **"Image-to-video or text-to-video?"** -- if I2V,
   ask for the source image path.

For monitoring/cron:

7. **"Where should I post progress updates?"** -- collect a destination from
   the user (Discord channel ID, log file, etc.) at batch startup. Do not
   hardcode this.

**Check for existing `joycaption.md` BEFORE generating prompts.** If found,
ask the user: "Found existing `joycaption.md` -- use it, update it, or start
fresh?"

---

## Pre-flight checks (run silently, surface only on failure)

Before queueing:

1. `comfyui_is_alive(host)` -- is the server reachable?
2. `/object_info` -- does the workflow's required node class exist?
3. Workflow file exists at the path the user gave.
4. Input folder has at least one image file (for I2I / I2V).
5. The user-owned paths (workflow file, input folder, output folder, model
   filenames) are all confirmed from this install, not from remembered defaults.

If any check fails, **stop and surface a clear message** naming the missing
item.

---

## Anti-scatter checks (before writing any file)

- Does this file type have a defined home in the table at the top of this file?
- Is there already a similar file in a standard location I should be using instead?
- Am I about to write a path or filename that depends on a specific user or
  machine? If yes, parameterize it.

If you find yourself thinking "I'll just put this here for now" -- stop.
Find the right location and put it there from the start.

---

## Why this matters

An agent dropped into this project with no context can navigate it correctly
because:

- Every file has a clear, singular purpose
- Layout is predictable (matches the table at the top)
- The only machine-specific values are the ones the user explicitly provided
  at runtime
- Demo workflows are explicitly marked as examples, not drop-ins

The alternative -- scattered docs, hardcoded paths, demo workflows presented as
production -- creates invisible cross-contamination where one user's setup
silently becomes another user's "the official way."

---

*This file is portable. The rules in it apply to any ComfyUI install on any
machine. The specific values (paths, models, channels) are always
runtime-supplied.*
