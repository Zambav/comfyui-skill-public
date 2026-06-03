# Changelog

## v1.4.0

### Added
- **`scripts/api_lib.py`** — battle-tested, path-agnostic ComfyUI API helper. Persistent WebSocket with thread-safe reconnect, queue/history/interrupt/clear helpers, env-var-configurable host (`COMFYUI_HOST`, `COMFYUI_WS`), and zero hardcoded machine paths.
- **`scripts/template_run_batch.py`** — sanitized batch-run starter script (FLUX 2 image edit). Reads the workflow from a user-supplied path, derives output and job folders from the input folder, uses env-var-configurable ComfyUI host. Replace the controller's `scripts/template_run_batch.py` for any public use.
- **`docs/joycaption-convention.md`** — formal JoyCaption naming, format, and pipeline convention. Documents the three naming variants (`joycaption.md`, `joycaption_{foldername}.md`, `joycaption_{asset_name}.md`), per-image `## filename.ext` heading format, description rules, and the LLM-driven prompt generation pipeline.
- **`AGENTS.md`** — AI agent cold-start instructions at the public-skill root. File placement rules, read path for a cold agent, hard rules (no absolute paths, no model filename assumptions, no notification destination assumptions, etc.), and the standardized intake questionnaire pattern.
- **FLUX 2 Image Gen (T2I) node map** in `reference-implementations.md` — the missing table for the `Flux 2 image gen` workflow (node `135` text prompt, node `94` SaveImage, etc.).
- **WAN 2.2 node map** in `reference-implementations.md` — typical skeleton, Animate variant extras, and asset-checklist guidance.
- **Hunyuan T2V node map** in `reference-implementations.md` — typical loader/encoder/VAE/sampler/output skeleton with node-class placeholders to be confirmed from `/object_info`.
- **FLUX T2I build helper** (`build_flux_t2i_workflow`) and **Hunyuan build helper** (`build_hunyuan_t2v_workflow`) in `reference-implementations.md`.
- **`derive_job_folder_dated` and `derive_temp_workflow_copy`** helpers in `reference-implementations.md` — date-prefixed job folder layout, recommended for production.
- **Intake Questionnaire** section in `batch-operations.md` — formal 8-question pattern for an agent to collect from the user (input folder, output, batch name, prompt, batch count, I2V/T2V, source image, notification destination). Replaces ad-hoc "ask two questions" guidance with a portable standard.

### Changed
- **`reference-implementations.md`** — added a Contents section; the API library section now points to `scripts/api_lib.py` as the production code and demotes the inline `ComfyUI` class to a fallback; the image resolution helpers section gains the dated job folder helpers.
- **`batch-operations.md`** — sanitized the state file example to use placeholder paths; added a recommended date-prefixed job folder layout alongside the legacy `Batch Jobs/{folder}_batch_job_{wf}/` layout; replaced the personal path references in the "Assumptions" section.
- **`cron-jobs.md`** — converted from Discord-specific to scheduler-agnostic. OpenClaw is shown as one possible scheduler (alongside `cron`, `launchd`, `systemd`); the notification destination is no longer assumed to be Discord (the agent asks the user). Removed all hardcoded channel IDs.
- **`SKILL.md`** — added JoyCaption-trigger and "check for existing joycaption.md" rule to the global operating rules; updated the read path to point at the new files; added the no-hardcoded-values rule.
- **`README.md`** — added the new files to the key capabilities, quick start, and repository structure sections.

## v1.3.0

### Added
- **cron-jobs.md** — Full batch monitoring SOP: Discord message templates (start, progress, completion, failure), progress field definitions (done, avg_time, eta, iph, errors, longest, shortest), cron setup procedure (ask for Discord channel first), error recovery sequence (assess → fix → report → retry, max 3 attempts), cron destroy rules, and quick reference command block

### Changed
- **batch-operations.md** — Expanded batch monitoring section with summary of key cron rules; now references `cron-jobs.md` for full monitoring SOP
- **SKILL.md** — Added `cron-jobs.md` to read-path routing under batch jobs

## v1.2.0

### Added
- **prompting-guides/flux-2-prompting-guide.md** — FLUX 2 prompt structure, model-aware best practices, and troubleshooting patterns
- **prompting-guides/wan-2.2-prompting-guide.md** — WAN 2.2 video prompting methodology, temporal sequencing, and motion/camera guidance
- **prompting-guides/README.md** — Prompt guide index table (model, use-case, link, last-updated)

### Changed
- Migrated prompting docs into **prompting-guides/** folder for centralized model-specific guidance
- Moved `prompting.md` to `prompting-guides/general-prompting-guide.md`
- Moved `prompting-guide-ltx.md` to `prompting-guides/ltx-2.3-prompting-guide.md`
- Updated internal references in `SKILL.md`, `README.md`, and `dependencies.md` to new prompting guide paths
- Added “which guide to use” decision flow in `SKILL.md`
- Expanded `setup.md` with first-time control readiness checks and setup completion criteria

## v1.1.0


### Added
- **prompting-guide-ltx.md** — Full LTX 2.3 official prompting guide covering specificity, scene direction, texture, I2V verb usage, static-prompt avoidance, portrait composition, audio description, shot categories, and sample prompts
- **batch-operations.md** — Queue-and-watch pattern, job state files, watchdog recovery, output folder naming, job folder structure, multi-batch management, and Python invocation guidance
- **reference-implementations.md** — FLUX image edit node map (all fixed/patched nodes), LTX 2.3 video node map, workflow patching patterns, full ComfyUI api_lib reference implementation with `queue_prompt`, `wait_for_completion`, `get_history`, `interrupt`, `clear_queue`, image resolution helpers, and prompt versioning standard
- **dependencies.md** — ComfyUI install, Python packages (`requests`, `websocket-client`, `pillow`), JoyCaption setup and pipeline role, RTX Video Super Resolution (optional), custom node packs, LLM requirements for prompt generation
- **LoRA training pipeline** — Referenced in SKILL.md triggers and routing; see `models.md` for LoRA loading and training guidance
- Updated `README.md` — New features highlighted, repository layout updated, key workflows documented (FLUX image edit, LTX video I2V/T2V, LLM-driven prompting pipeline, LoRA training)
- Updated `SKILL.md` — Added LoRA training triggers, updated read paths to all new files, expanded trigger scope

## v1.0.0

- Created a public, portable ComfyUI skill package derived from a machine-specific source skill
- Reduced `SKILL.md` to trigger logic, scope, and routing
- Moved detailed guidance into per-topic files
- Replaced personal model inventories and private naming with discovery-first patterns
- Reframed setup from "configured on this machine" to "unknown install, discover first"
- Added onboarding and config-template references for first-run setup
- Added a cold-read test to catch hidden assumptions before packaging
