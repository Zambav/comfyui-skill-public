# Changelog

## v1.1.0

### Added
- **prompting-guide-ltx.md** — Full LTX 2.3 official prompting guide covering specificity, scene direction, texture, I2V verb usage, static-prompt avoidance, portrait composition, audio description, shot categories, and sample prompts
- **batch-operations.md** — Queue-and-watch pattern, job state files, watchdog recovery, output folder naming, job folder structure, multi-batch management, and Python invocation guidance
- **reference-implementations.md** — FLUX image edit node map (all fixed/patched nodes), LTX 2.3 video node map, workflow patching patterns, full ComfyUI api_lib reference implementation with `queue_prompt`, `wait_for_completion`, `get_history`, `interrupt`, `clear_queue`, image resolution helpers, and prompt versioning standard
- **dependencies.md** — ComfyUI install, Python packages (`requests`, `websocket-client`, `pillow`), JoyCaption setup and pipeline role, RTX Video Super Resolution (optional), custom node packs, LLM requirements for prompt generation
- **LoRA training pipeline** — Referenced in SKILL.md triggers and routing; see `lora.md` for training configuration
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
