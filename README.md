# comfyui-skill-public

> **Control ComfyUI with natural language — directly from your AI agent.**

Build workflows, queue batch jobs, generate images and videos, debug graphs, and train LoRAs — without leaving chat. No hardcoded paths. No machine-specific assumptions. Works across local, remote, and cloud ComfyUI installs.

---

## What you can do with this skill

- **Generate images from chat** — describe what you want and the agent builds and submits the workflow
- **Generate videos** — image-to-video (I2V) and text-to-video (T2V) with LTX 2.3
- **Create and modify workflows with natural language** — no manual JSON editing required
- **Queue batch jobs** — run prompt sweeps, campaign sets, or variant batches with state tracking and automatic recovery
- **Auto-discover your install** — the skill queries your live ComfyUI server before authoring anything
- **Train LoRAs** — full training pipeline from dataset preparation through checkpoint management
- **Troubleshoot broken graphs** — paste an error, get a diagnosis and a fix
- **Add LoRAs, swap models, chain nodes** — describe the change and the agent handles the graph surgery
- **LLM-driven custom prompting** — JoyCaption images, then use an LLM to generate unique cinematic prompts per image
- **Validate before you run** — compatibility checks catch model family mismatches before they waste GPU time

---

## What's new

- **LTX 2.3 video support** — dedicated prompting guide, I2V/T2V node maps, and batch video generation
- **LLM-driven prompting pipeline** — non-destructive workflow: JoyCaption descriptions → LLM generates cinematic prompts → batch runner loads from JSON
- **Batch operations guide** — queue-and-watch pattern, job state files, watchdog recovery, and multi-batch management
- **Reference implementations** — proven FLUX image edit and LTX video node maps, patching patterns, and full api_lib reference implementation
- **LoRA training pipeline** — dataset structuring, training configuration, checkpoint management, and deployment

---

## Getting started

1. Clone or download this repo into your OpenClaw skills environment as `comfyui-skill-public`
2. Open `SKILL.md` — it defines the trigger scope and routing behavior for your agent
3. For a fresh install, start with `setup.md`
4. Collect your install-specific values using `config-template.md`
5. Install dependencies from `dependencies.md` (ComfyUI, Python packages, JoyCaption)
6. Start talking to your agent

---

## Repository layout

```
comfyui-skill-public/
├── SKILL.md                         # Trigger scope, routing, global rules
├── README.md                        # This file
├── prompting-guide-ltx.md            # LTX 2.3 model-specific prompting (comprehensive)
├── batch-operations.md               # Queue management, state files, recovery, monitoring
├── reference-implementations.md      # FLUX + LTX node maps, patching patterns, api_lib
├── dependencies.md                   # ComfyUI, JoyCaption, Python packages, optional nodes
├── demo-workflows/                   # Example workflow JSON files (see disclaimer below)
│   ├── README.md                     # READ BEFORE USE — not for production
│   ├── Flux 2 Image edit workflow API/
│   ├── Flux 2 image gen/
│   └── ltx 2.3/
├── setup.md                         # First-time onboarding for unknown installs
├── api.md                           # REST/WebSocket API usage patterns
├── workflow-patterns.md             # Graph construction and validation
├── models.md                        # Family-specific model guidance
├── compatibility.md                 # Mismatch prevention checks
├── lora.md                          # LoRA compatibility, tuning, and training
├── prompting.md                     # Portable prompting guidance (general)
├── graph-conventions.md             # Graph hygiene and debugging checklist
├── config-template.md               # User-owned setup record template
├── changelog.md                     # Release history
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── LICENSE
```

### About demo-workflows/

> **These workflow JSON files are for demonstration purposes only.** They were built for a specific ComfyUI install with custom nodes and machine-specific model paths. They will NOT work as-is on another machine. Export your own workflows from your ComfyUI instance and adapt them using the node maps in `reference-implementations.md`. See `demo-workflows/README.md` for full details.

---

## Key workflows

### Image generation (FLUX)

```
You: "edit these photos to look cinematic"
Agent asks: "What's the prompt?" + "One batch or multiple?"
You: "enhance with warm lighting, film grain"
Agent: runs FLUX image edit batch → outputs next to source images
```

### Video generation (LTX 2.3 I2V/T2V)

```
You: "make a video of this image with a slow push-in"
Agent asks: prompt + I2V or T2V + output filename
You: "slow push-in, subject turns to camera, golden hour"
Agent: copies image to ComfyUI input/, queues job, blocks on completion
```

### LLM-driven custom prompting (LTX video)

```
JoyCaption → captions.txt (raw scene descriptions, never touched)
     ↓
LLM reads: captions.txt + prompting-guide-ltx.md
     ↓
ltx_video_prompts.json (unique cinematic prompt per image, versioned)
     ↓
run_ltx_video_batch.py loads JSON → queues to ComfyUI
```

See `batch-operations.md` for the full non-destructive pipeline.

### LoRA training

```
You: "train a LoRA on this dataset"
Agent: helps structure dataset folder, configures training parameters,
       manages checkpoint output, deploys to ComfyUI
```

See `lora.md` for training configuration and compatibility.

---

## ComfyUI API endpoints used

| Endpoint | Purpose |
|---|---|
| `GET /object_info` | Discover available nodes and their inputs |
| `POST /prompt` | Submit a workflow to the queue |
| `GET /queue` | Monitor queue state |
| `GET /history/{prompt_id}` | Retrieve run results and output metadata |
| `POST /interrupt` | Stop a running job |
| `GET /system_stats` | Health check |
| `WS /ws` | Real-time queue and progress events |

---

## Troubleshooting

**Missing node class errors**
Check `GET /object_info` for the required class. If absent, the custom node isn't installed. The agent stops early and reports exactly what's missing.

**Model or LoRA not found**
Filename and dropdown values are discovered from your live install — the skill never assumes your model inventory. Verify the exact filename matches what's on disk.

**Workflow submits but fails mid-run**
Validate encoder/VAE/scheduler compatibility for your model family. Check `GET /history/{prompt_id}` for the concrete error. Reduce to the smallest failing component.

**Batch jobs failing silently**
Use the queue-and-watch pattern — always block on WebSocket completion and verify with `/history`. See `batch-operations.md` for state file and recovery patterns.

**Output retrieval issues**
Outputs are resolved from history metadata, not hardcoded paths. For hosted deployments where `/view` is unavailable, use platform-specific output mechanisms.

**Remote or cloud connectivity**
Confirm base URL and WebSocket URL are reachable. Where WebSocket is unavailable, the skill falls back to polling queue/history.

---

## Security notes

- Absolute filesystem paths are never embedded in reusable workflows
- Install-specific values live in user-owned config, not in skill defaults
- Secrets and API tokens are never stored in skill docs or workflow JSON
- Capabilities are always validated from live install data before submitting expensive jobs
- Model files and LoRAs must be obtained separately — none are included in this repo

---

## License

MIT — see [LICENSE](LICENSE)
