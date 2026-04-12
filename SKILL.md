---
name: comfyui-skill-public
description: Portable ComfyUI workflow and API guidance for any install. Use when building, validating, or troubleshooting ComfyUI image/video workflows, discovering available nodes/models via /object_info, wiring loaders/encoders/VAEs/LoRAs correctly, submitting jobs through the REST or WebSocket APIs, training LoRAs with ComfyUI, adapting a workflow to an unknown user machine without assuming specific checkpoints, paths, hardware, or custom nodes.
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
- "Train a LoRA on this dataset"
- "Run a batch on these images"
- "Generate a video with LTX"
- "Edit these photos with FLUX"
- "Run a video batch"
- "JoyCaption these images and generate prompts"

## First move: assume zero install knowledge

Before writing or editing any workflow:
1. Read [setup.md](setup.md) if the install is unknown.
2. Collect the missing setup fields from the user or discover them from the running ComfyUI instance via `/object_info`.
3. Prefer discovery over assumptions — confirm checkpoints, VAEs, encoders, and LoRAs from the target install.
4. Stop and report missing requirements clearly.

## Read path by task

- Setup / first run / portability questions -> [setup.md](setup.md)
- LTX 2.3 video or image-to-video generation -> [prompting-guide-ltx.md](prompting-guide-ltx.md)
- Batch jobs with state tracking and recovery -> [batch-operations.md](batch-operations.md)
- FLUX image edit nodes, LTX video nodes, api_lib reference -> [reference-implementations.md](reference-implementations.md)
- Demo workflow JSON files (FLUX image edit, LTX video) -> [demo-workflows/](demo-workflows/) — **for demonstration only; replace with your own workflows**
- External dependencies (JoyCaption, ComfyUI, Python packages) -> [dependencies.md](dependencies.md)
- API submission / queue / history / WebSocket -> [api.md](api.md)
- Programmatic graph building, compatibility checks, and debugging -> [workflow-patterns.md](workflow-patterns.md)
- Model-family requirements and LoRA loading/training guidance -> [models.md](models.md)
- Prompt construction (general) -> [prompting.md](prompting.md)
- Release history -> [changelog.md](changelog.md)

## Global operating rules

- Treat node classes as discoverable, not guaranteed constants.
- Treat model filenames as examples until confirmed on the target install.
- Use filename-only model references in workflow JSON unless the install explicitly requires a subdirectory path.
- Use defensive parsing for `/history` and `/object_info`; schema details can vary by ComfyUI version and custom nodes.
- Fail fast when a required node class, model, or custom node is missing.
- Keep setup-specific notes out of this file; put them in a per-user config or setup reference.
- Never edit a base workflow JSON file directly — always deep copy and patch.
- Demo workflow JSON files in [demo-workflows/](demo-workflows/) are provided as working examples. Replace them with your own workflows adapted to your ComfyUI install.

## Cold-read test

Before publishing or packaging changes, check that a fresh reader could answer:
- What does this skill do?
- When should it trigger?
- What must be discovered first?
- Where do install-specific values go?
- Which reference file should be opened for the current task?
