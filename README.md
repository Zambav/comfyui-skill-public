# comfyui-skill-public

Portable ComfyUI workflow + API guidance for unknown or mixed environments.

This repository packages an OpenClaw-ready skill that helps agents and users build, validate, troubleshoot, and run ComfyUI workflows without assuming machine-specific paths, model inventories, GPUs, or custom node sets.

## What this skill is

`comfyui-skill-public` is a **discovery-first ComfyUI operations skill**. It is designed to:

- Work across local, remote, and cloud ComfyUI installs
- Discover node/model capabilities from the target server (`/object_info`) before workflow authoring
- Prevent cross-family graph mistakes (SDXL, FLUX, WAN, LTX)
- Guide API submission, queue monitoring, history parsing, and output retrieval
- Keep setup facts user-owned and separate from reusable guidance

## Repository layout

- `SKILL.md` — trigger scope, routing, global rules
- `references/setup.md` — startup/onboarding flow for unknown installs
- `references/api.md` — REST/WebSocket API usage pattern
- `references/workflow-patterns.md` — graph construction and validation patterns
- `references/models.md` — family-specific model guidance
- `references/compatibility.md` — mismatch prevention checks
- `references/lora.md` — LoRA compatibility and tuning guidance
- `references/graph-conventions.md` — graph hygiene and debugging checklist
- `references/config-template.md` — user-owned setup record template
- `references/prompting.md` — portable prompting guidance

## Quick start

1. Copy this skill into your skills environment and expose it as `comfyui-skill-public`.
2. Open `SKILL.md` and follow the trigger scope/routing behavior.
3. For first-time setup on a target server, start with `references/setup.md`.
4. Collect only the minimum required user facts, then discover capabilities from the ComfyUI API:
   - `GET /object_info`
   - `POST /prompt`
   - `GET /queue`
   - `GET /history` or `GET /history/{prompt_id}`
   - WebSocket `/ws` (when available)
5. Store install-specific values in a user-owned config based on `references/config-template.md`.

## Trigger examples

Use this skill for prompts like:

- "Build a ComfyUI workflow"
- "Fix this ComfyUI workflow"
- "Use the ComfyUI API"
- "Why is this ComfyUI graph failing?"
- "Add a LoRA / model / node to this ComfyUI setup"
- "Adapt this graph to my remote ComfyUI instance"

## Common troubleshooting

### 1) Missing node class errors
- Re-check `GET /object_info` for required node classes.
- Confirm needed custom nodes are installed on the target server.
- Stop early and report exactly which class is missing.

### 2) Model or LoRA filename not found
- Confirm dropdown values from the target install (do not assume local inventory).
- Verify model family compatibility (e.g., LoRA training family vs base model family).

### 3) Workflow submits but fails during run
- Validate encoder/VAE/scheduler compatibility for the selected model family.
- Check `GET /history/{prompt_id}` and queue state for concrete failure reason.
- Reduce to smallest failing graph and reintroduce components incrementally.

### 4) Output retrieval issues
- Resolve outputs from history metadata instead of hardcoded filesystem paths.
- If `/view` is unavailable in a hosted deployment, use the platform-specific output path mechanism.

### 5) Remote/cloud connectivity issues
- Confirm base URL and websocket URL are correct and reachable.
- Handle environments where WebSocket is unavailable by polling queue/history.

## Why this is useful

### Batch jobs
- Queue large prompt sets and monitor run progress reliably.
- Useful for campaign generation, variant sweeps, and throughput workflows.

### Workflow testing/regression checks
- Validate the same workflow across upgrades/custom-node changes.
- Catch breakages early by confirming node/model availability before submit.

### LoRA iteration and dataset workflows
- Systematically test LoRA combinations with conservative strengths.
- Useful for model tuning loops and comparing style/performance consistency.

### Portable automation
- One process works across local desktop ComfyUI, remote hosts, and cloud deployments.
- Reduces failure from hardcoded assumptions and machine-specific graph logic.

## Security and privacy posture

- Avoid absolute filesystem paths in reusable workflows.
- Treat install-specific values as user-owned config, not skill defaults.
- Do not embed secrets/tokens in skill docs or workflow JSON.
- Validate requirements from live install data before running expensive jobs.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
