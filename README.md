# comfyui-skill-public

> **Control ComfyUI with natural language — directly from OpenClaw.**

Build workflows, queue batch jobs, generate images, and debug graphs without ever leaving chat. No hardcoded paths. No machine-specific assumptions. Works across local, remote, and cloud ComfyUI installs.

---

## What you can do with this skill

Once installed, your OpenClaw agent can handle ComfyUI end-to-end through conversation:

- **Generate images from chat** — describe what you want and the agent builds and submits the workflow
- **Create and modify workflows with natural language** — no manual JSON editing required
- **Queue batch jobs** — run prompt sweeps, campaign sets, or variant batches and monitor them in real time
- **Auto-discover your install** — the skill queries your live ComfyUI server before authoring anything, so it always works with what you actually have installed
- **Troubleshoot broken graphs** — paste an error, get a diagnosis and a fix
- **Add LoRAs, swap models, chain nodes** — describe the change and the agent handles the graph surgery
- **Validate before you run** — compatibility checks catch SDXL/FLUX/WAN family mismatches before they waste GPU time

This skill is designed to be **portable**. The same workflow works whether you're running ComfyUI on your local desktop, a remote server, or a cloud deployment.

---

## Getting started

1. Clone or download this repo and drop it into your OpenClaw skills environment as `comfyui-skill-public`
2. Open `SKILL.md` — it defines the trigger scope and routing behavior for your agent
3. For a fresh install, start with `references/setup.md` — it walks through first-time server discovery
4. Collect your install-specific values (base URL, model names, etc.) using `references/config-template.md`
5. Start talking to your agent

The skill discovers everything it needs from your live server via the ComfyUI API — it never assumes what models, nodes, or custom extensions you have.

---

## Key use cases

### 🖼 Image generation from chat
Ask your agent to generate an image. It builds the workflow, submits it, monitors the queue, and returns the output — all from a single prompt.

### 🔁 Batch jobs and variant sweeps
Queue large sets of prompts for campaign generation, A/B style testing, or LoRA comparison runs. Monitor progress and retrieve outputs without touching the UI.

### 🔧 Workflow authoring and repair
Describe the graph you want or paste a broken one. The agent constructs, validates, and corrects it — checking node availability and model compatibility first.

### 🎨 LoRA testing and iteration
Systematically test LoRA combinations at conservative strengths. Useful for tuning loops, style comparisons, and archviz/character consistency workflows.

### 🚀 Remote and cloud deployments
One skill, any ComfyUI instance. No hardcoded paths or local assumptions — connect to a remote host or cloud GPU and it just works.

---

## Repository layout

```
comfyui-skill-public/
├── SKILL.md                        # Trigger scope, routing, global rules
└── references/
    ├── setup.md                    # First-time onboarding for unknown installs
    ├── api.md                      # REST/WebSocket API usage patterns
    ├── workflow-patterns.md        # Graph construction and validation
    ├── models.md                   # Family-specific model guidance
    ├── compatibility.md            # Mismatch prevention checks
    ├── lora.md                     # LoRA compatibility and tuning
    ├── graph-conventions.md        # Graph hygiene and debugging checklist
    ├── config-template.md          # User-owned setup record template
    └── prompting.md                # Portable prompting guidance
```

---

## ComfyUI API endpoints used

| Endpoint | Purpose |
|---|---|
| `GET /object_info` | Discover available nodes and their inputs |
| `POST /prompt` | Submit a workflow to the queue |
| `GET /queue` | Monitor queue state |
| `GET /history/{prompt_id}` | Retrieve run results and output metadata |
| `WS /ws` | Real-time queue and progress events |

---

## Troubleshooting

**Missing node class errors**
Check `GET /object_info` for the required class. If it's absent, the custom node isn't installed on the target server. The agent will stop early and report exactly what's missing.

**Model or LoRA not found**
Filename and dropdown values are discovered from your live install — the skill never assumes your model inventory. Verify the exact filename matches what's on disk.

**Workflow submits but fails mid-run**
Validate encoder/VAE/scheduler compatibility for your model family. Check `GET /history/{prompt_id}` for the concrete error. The agent can reduce the graph to the smallest failing component and rebuild from there.

**Output retrieval issues**
Outputs are resolved from history metadata, not hardcoded paths. For hosted deployments where `/view` is unavailable, use the platform-specific output mechanism.

**Remote or cloud connectivity**
Confirm base URL and WebSocket URL are reachable. In environments where WebSocket is unavailable, the skill falls back to polling queue/history.

---

## Security notes

- Absolute filesystem paths are never embedded in reusable workflows
- Install-specific values live in user-owned config, not in skill defaults
- Secrets and API tokens are never stored in skill docs or workflow JSON
- Capabilities are always validated from live install data before submitting expensive jobs

---

## License

MIT — see [LICENSE](LICENSE)
