# comfyui-skill-public

> **Control ComfyUI with natural language — directly from your AI agent.**

Build workflows, queue batch jobs, generate images and videos, debug graph failures, and run a full LoRA training pipeline from chat. This repo is portable by design: no hardcoded paths, no machine-specific assumptions, and no fixed model inventory.

---

## Why this repo exists

`comfyui-skill-public` gives agents a clean, reusable operating model for ComfyUI across local, remote, and cloud installs:
- discover capabilities from live `/object_info`
- build and patch workflows safely
- submit and monitor jobs through REST/WebSocket APIs
- run repeatable batch and recovery patterns
- support LoRA loading and training with JoyCaption capabilities and dynamic prompting

---

## Key capabilities

- **Natural-language workflow control** — create, modify, and debug ComfyUI workflows without manual JSON edits
- **Image + video generation** — FLUX image workflows and LTX 2.3 I2V/T2V workflows
- **Batch execution patterns** — queue-and-watch flow, state files, retry/recovery behavior
- **Portability-first validation** — compatibility checks before expensive runs
- **LoRA training pipeline** — dataset structuring, training config, JoyCaption-assisted descriptions, dynamic prompting, checkpoint management, and ComfyUI deployment

---

## Quick start

1. Clone this repo into your skills environment as `comfyui-skill-public`
2. Read `SKILL.md` to understand trigger scope and routing
3. For unknown installs, complete onboarding in `setup.md`
4. Install runtime dependencies from `dependencies.md`
5. Start issuing ComfyUI tasks to your agent

---

## Common workflows

### FLUX image workflow

```text
You: "edit these photos to look cinematic"
Agent asks: "What's the prompt?" + "One batch or multiple?"
You: "enhance with warm lighting, film grain"
Agent: runs FLUX batch workflow and writes outputs next to source images
```

### LTX 2.3 video workflow (I2V/T2V)

```text
You: "make a video of this image with a slow push-in"
Agent asks: prompt + I2V or T2V + output filename
You: "slow push-in, subject turns to camera, golden hour"
Agent: stages input, queues job, blocks on completion, returns outputs
```

### LoRA training workflow

```text
You: "train a LoRA on this dataset"
Agent: helps structure dataset folders, configures training parameters,
       uses JoyCaption capabilities where needed, applies dynamic prompting,
       manages checkpoint output, and deploys to ComfyUI
```

For training and compatibility details, see `models.md`.

---

## Pipeline overview

### LLM-driven prompting pipeline (video)

```text
JoyCaption -> captions.txt (raw scene descriptions, never modified)
      ↓
LLM reads captions.txt + prompting-guide-ltx.md
      ↓
ltx_video_prompts.json (versioned, unique prompt per image)
      ↓
Batch runner loads JSON -> queues to ComfyUI
```

### LoRA training pipeline (expanded)

```text
Dataset prep -> JoyCaption-assisted descriptions -> dynamic prompting variants
      ↓
Training config + run -> checkpoint management
      ↓
Deploy selected checkpoint to ComfyUI
```

---

## Repository structure

```text
comfyui-skill-public/
├── SKILL.md
├── README.md
├── setup.md
├── api.md
├── workflow-patterns.md
├── models.md
├── dependencies.md
├── prompting.md
├── prompting-guide-ltx.md
├── batch-operations.md
├── reference-implementations.md
├── demo-workflows/
├── changelog.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
└── LICENSE
```

> Demo workflows are examples only and may depend on machine-specific nodes/models. See `demo-workflows/README.md` before use.

---

## Troubleshooting

- **Missing node class**: confirm class availability in `GET /object_info`
- **Model or LoRA not found**: verify exact filename from the target install
- **Run fails mid-graph**: validate family-specific encoder/VAE/scheduler compatibility
- **Batch appears stalled**: use queue-and-watch + `/history` verification
- **Cloud/remote issues**: confirm REST and WebSocket reachability

---

## Project standards

- Security policy: `SECURITY.md`
- Contribution guide: `CONTRIBUTING.md`
- Code of conduct: `CODE_OF_CONDUCT.md`

## License

MIT — see [LICENSE](LICENSE)
