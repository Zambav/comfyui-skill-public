---
name: comfyui-skill-public
description: Portable ComfyUI workflow and API guidance for any install. Use when building, validating, or troubleshooting ComfyUI image/video workflows, discovering available nodes/models via /object_info, wiring loaders/encoders/VAEs/LoRAs correctly, submitting jobs through the REST or WebSocket APIs, or adapting a workflow to an unknown user machine without assuming specific checkpoints, paths, hardware, or custom nodes.
---

# ComfyUI Portable Skill

Use this skill when the task is to work with ComfyUI in a reusable, installation-agnostic way.

## Minimum trigger scope

Trigger on requests like:
- "Build a ComfyUI workflow"
- "Fix this ComfyUI workflow"
- "Use the ComfyUI API"
- "Why is this ComfyUI graph failing?"
- "Add a LoRA / model / node to this ComfyUI setup"

Do not assume any particular machine, model inventory, file layout, GPU, or custom node pack.

## First move: assume zero install knowledge

Before writing or editing any workflow:
1. Read [references/setup.md](references/setup.md).
2. If the install is unknown, collect the missing setup fields from the user or discover them from the running ComfyUI instance.
3. Prefer discovery over assumptions:
   - use `/object_info` to detect node classes and model dropdown values
   - confirm checkpoints, VAEs, encoders, and LoRAs from the target install
   - stop and report missing requirements clearly

## Read path by task

- Setup / first run / portability questions -> [references/setup.md](references/setup.md)
- API submission / queue / history / WebSocket -> [references/api.md](references/api.md)
- Programmatic graph building -> [references/workflow-patterns.md](references/workflow-patterns.md)
- Model-family requirements -> [references/models.md](references/models.md)
- Cross-family validation / node availability -> [references/compatibility.md](references/compatibility.md)
- LoRA loading and compatibility -> [references/lora.md](references/lora.md)
- Prompt construction -> [references/prompting.md](references/prompting.md)
- Graph hygiene / debugging -> [references/graph-conventions.md](references/graph-conventions.md)
- Release history -> [references/changelog.md](references/changelog.md)
- User-fill config template -> [references/config-template.md](references/config-template.md)

## Global operating rules

- Treat node classes as discoverable, not guaranteed constants.
- Treat model filenames as examples until confirmed on the target install.
- Use filename-only model references in workflow JSON unless the install explicitly requires a subdirectory path.
- Use defensive parsing for `/history` and `/object_info`; schema details can vary by ComfyUI version and custom nodes.
- Fail fast when a required node class, model, or custom node is missing.
- Keep setup-specific notes out of this file; put them in a per-user config or setup reference.

## Cold-read test

Before publishing or packaging changes, check that a fresh reader could answer:
- What does this skill do?
- When should it trigger?
- What must be discovered first?
- Where do install-specific values go?
- Which reference file should be opened for the current task?
