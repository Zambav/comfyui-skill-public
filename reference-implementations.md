# Reference Implementations

> Portable, proven code patterns for ComfyUI integration. These are reference implementations — adapt paths, node IDs, and configuration to the target install.
>
> **Demo workflow JSON files** are provided in [demo-workflows/](demo-workflows/) as working examples. These are tied to a specific install and are **not for production use** — export your own from your ComfyUI and adapt the patterns here. See `demo-workflows/README.md` for details.
>
> **Production helper:** a battle-tested, path-agnostic `api_lib.py` is shipped at [scripts/api_lib.py](scripts/api_lib.py). Prefer importing it (or copying the patterns) over re-deriving them from the snippets below.

---

## Contents

- [FLUX 2 Image Edit — Node Map](#flux-image-edit--node-map)
- [FLUX 2 Image Gen (T2I) — Node Map](#flux-2-image-gen-t2i--node-map)
- [LTX 2.3 Video — Node Map](#ltx-23-video--node-map)
- [WAN 2.2 Video — Node Map](#wan-22-video--node-map)
- [Hunyuan T2V — Node Map](#hunyuan-t2v--node-map)
- [Workflow Loading and Patching Pattern](#workflow-loading-and-patching-pattern)
- [API Library — Reference Implementation](#api-library--reference-implementation)
- [Image Resolution Helpers](#image-resolution-helpers)
- [Prompt Versioning for LLM-Generated Prompts](#prompt-versioning-for-llm-generated-prompts)

---

## FLUX Image Edit — Node Map

| Node ID | Class | Role | Action |
|---|---|---|---|
| `6` | CLIPTextEncode | **Edit prompt** | ✏️ PATCH — the instruction text |
| `163` | KSampler | Sampler seed | ✏️ PATCH — per-image variation seed |
| `164` | VAEDecode | Decode latent | fixed |
| `190` | ConditioningZeroOut | Auto-zero negative | fixed |
| `194` | UNETLoader | FLUX 2 Klein 9B KV FP8 | fixed |
| `195` | CLIPLoader | Qwen 3 8B text encoder | fixed |
| `196` | VAELoader | flux2-vae | fixed |
| `197` | EmptyFlux2LatentImage | Latent canvas | fixed |
| `198` | LoadImage | **Input image** | ✏️ PATCH — source filename (copy to ComfyUI input/ first) |
| `199` | ImageScaleToTotalPixels | Normalize to 2MP | fixed |
| `200` | GetImageSize | Read dimensions | fixed |
| `202` | Image Comparer (rgthree) | UI preview | fixed |
| `203` | SaveImage | Secondary save | fixed |
| `204` | ReferenceLatent | Positive ref | fixed |
| `205` | ReferenceLatent | Negative ref | fixed |
| `206` | VAEEncode | Encode input image | fixed |
| `212` | FluxKVCache | KV cache | fixed |
| `213` | RTXVideoSuperResolution | 2× RTX upscale | fixed |
| `214` | Image Comparer (rgthree) | RTX UI preview | fixed |
| `216` | InpaintStitchImproved | Stitch passthrough | fixed |
| `221:217` | InpaintCropImproved | Crop passthrough | fixed |
| `225` | ttN imageOutput | **Primary output** | ✏️ PATCH — `output_path`, `save_prefix`, `file_type` |

> **Rule: Override only nodes marked ✏️ PATCH. Everything else is fixed infrastructure. Never edit the base workflow JSON file.**

### Image Path Rule

ComfyUI resolves filenames relative to its own `input/` directory. Copy the source image there before queuing. Pass **filename only** — never an absolute path — to node 198.

```python
import shutil, os

def copy_to_comfyui_input(image_path: str, comfyui_input_dir: str) -> str:
    filename = os.path.basename(image_path)
    shutil.copy2(image_path, os.path.join(comfyui_input_dir, filename))
    return filename
```

---

## FLUX 2 Image Gen (T2I) — Node Map

Workflow file: `Flux 2 image gen.json`

| Node ID | Class | Role | Action |
|---------|-------|------|--------|
| `94` | SaveImage | **Output** | ❌ DO NOT TOUCH (auto-saves to `output/Flux2_Klein_9b_kv/`) |
| `122` | KSamplerSelect | Sampler select | ❌ DO NOT TOUCH |
| `123` | SamplerCustomAdvanced | Sampler | ❌ DO NOT TOUCH |
| `124` | VAEDecode | Decode latent | ❌ DO NOT TOUCH |
| `125` | RandomNoise | Noise seed | ❌ DO NOT TOUCH |
| `126` | UNETLoader | FLUX 2 diffusion model | ❌ DO NOT TOUCH |
| `127` | VAELoader | flux2-vae | ❌ DO NOT TOUCH |
| `129` | EmptyFlux2LatentImage | Latent canvas | ❌ DO NOT TOUCH |
| `133` | CLIPLoader | FLUX 2 text encoder | ❌ DO NOT TOUCH |
| `135` | CLIPTextEncode | **Text prompt** | ✏️ PATCH `inputs.text` |
| `137` | Flux2Scheduler | Scheduler | ❌ DO NOT TOUCH |
| `138` | CFGGuider | CFG | ❌ DO NOT TOUCH |
| `139` | FluxKVCache | KV cache | ❌ DO NOT TOUCH |
| `685` | ConditioningZeroOut | Auto-zero negative | ❌ DO NOT TOUCH |
| `698` | Any Switch (rgthree) | Model switch | ❌ DO NOT TOUCH |
| `725` | INTConstant | Width | ❌ DO NOT TOUCH |
| `726` | INTConstant | Height | ❌ DO NOT TOUCH |
| `727` | Any Switch (rgthree) | Width selector | ❌ DO NOT TOUCH |
| `728` | Any Switch (rgthree) | Height selector | ❌ DO NOT TOUCH |

**T2I patching rule:** Only node `135` needs patching. Set `inputs.text` to
your prompt. There is no input image, and no output path override — node 94
saves directly to ComfyUI's `output/` directory.

### Output location

The default `SaveImage` (node 94) writes to a ComfyUI-managed subfolder under
`output/`. If you need a different output location, swap node 94 for an
`ttN imageOutput` or other save node, or run a post-job `shutil.move` step
in your batch script.

---

## LTX 2.3 Video — Node Map

Workflow file: `LTX 2.3 Video I2V_T2V_ZAM.json`

| Node ID | Class | Title | Patch |
|---|---|---|---|
| `267:266` | PrimitiveStringMultiline | Prompt | ✏️ PATCH `inputs.value` — the text prompt |
| `269` | LoadImage | Load Image | ✏️ PATCH `inputs.image` — source filename (copy to ComfyUI input/ first) |
| `75` | SaveVideo | Save Video | ✏️ PATCH `inputs.filename_prefix` — output path + name stem |
| `267:201` | PrimitiveBoolean | Switch to Text to Video? | ✏️ PATCH `inputs.value`: `false` = I2V, `true` = T2V |

**Fixed reference values (do not patch unless asked):**
**Fixed reference values (do not patch unless asked):**
| Node | Value | Role |
|---|---|---|
| `267:257` | 1280 | Width |
| `267:258` | 720 | Height |
| `267:260` | 24 | Frame rate |
| `267:225` | 121 | Length (frames) |

### Output Path Rule

`filename_prefix` is relative to ComfyUI's `output/` directory. `video/car_reel` → `output/video/car_reel_00001.mp4`. **Always use a unique prefix per project** to avoid overwriting previous outputs.

---

## WAN 2.2 Video — Node Map

WAN 2.2 is a family of video models with several variants: T2V (text-to-video), I2V (image-to-video), Animate (character animation with pose/relighting), and Lightning (fast distilled variants). Confirm from `/object_info` which loader node and diffusion model your install expects — node IDs differ between variants.

### Common loader / sampler pattern (typical WAN 2.2 graph)

| Component | Role | Patch? |
|-----------|------|--------|
| `WanVideoModelLoader` (or equivalent) | Loads the diffusion model file | ❌ DO NOT TOUCH |
| `CLIPLoader` (umt5-xxl) | Text encoder | ❌ DO NOT TOUCH |
| `VAELoader` (Wan2.1 or Wan2.2 VAE) | VAE | ❌ DO NOT TOUCH |
| `CLIPTextEncode` (prompt) | **Text prompt** | ✏️ PATCH `inputs.text` |
| `LoadImage` (I2V / Animate) | **Source image** | ✏️ PATCH `inputs.image` (filename only) |
| `SaveVideo` (or `VHS_VideoCombine`) | **Output** | ✏️ PATCH `inputs.filename_prefix` |

> **Discovery-first:** WAN 2.2 variants have very different node maps. The table
> above shows the typical skeleton; the exact node IDs and class names must
> be confirmed from `/object_info` on the target install. If your install
> uses a community wrapper (e.g. `ComfyUI-WanVideoWrapper`), the node class
> names will differ from the upstream ComfyUI versions.

### Animate-specific extras

The Animate variant adds:

- `OnnxDetectionLoader` (or equivalent) — pose / detection model
- `ImagePoseDetection` or similar — extracts pose guidance
- `LoadImage` for the character reference
- Optional relighting LoRA loader (e.g. `WanAnimate_relight_lora`)

> **Asset checklist for Animate:** pose/detection model (`vitpose-l-wholebody.onnx` or similar), YOLO model (`yolo11x-pose.pt` or similar), and SAM2 weights must be present. Use an asset-audit script (see `scripts/asset_audit_template.md` if you ship one) to confirm before queueing.

### WAN 2.2 output path rule

Same as LTX: `filename_prefix` is relative to ComfyUI's `output/`. Always
unique per project. WAN outputs are larger than LTX (14B diffusion, longer
clips) — confirm disk space before batch runs.

---

## Hunyuan T2V — Node Map

Hunyuan Video is Tencent's text-to-video model family. A typical Hunyuan T2V
workflow has this skeleton:

| Component | Role | Patch? |
|-----------|------|--------|
| `HunyuanVideoModelLoader` (or equivalent) | Loads the diffusion model | ❌ DO NOT TOUCH |
| `DualCLIPLoader` (or `CLIPLoader`) | Hunyuan text encoder pair | ❌ DO NOT TOUCH |
| `VAELoader` (Hunyuan VAE) | VAE | ❌ DO NOT TOUCH |
| `CLIPTextEncode` (positive prompt) | **Text prompt** | ✏️ PATCH `inputs.text` |
| `CLIPTextEncode` (negative prompt) | Negative prompt | ✏️ PATCH `inputs.text` |
| `EmptyHunyuanLatentVideo` | Latent canvas (frames × H × W) | ❌ DO NOT TOUCH |
| `KSampler` (advanced) | Sampler | ❌ DO NOT TOUCH |
| `VAEDecode` | Decode latent | ❌ DO NOT TOUCH |
| `VHS_VideoCombine` (or `SaveVideo`) | **Output** | ✏️ PATCH `inputs.frame_rate`, `inputs.filename_prefix` |

### Hunyuan output path rule

`filename_prefix` is relative to ComfyUI's `output/`. Hunyuan videos are
typically 720×1280, 24fps, ~5s clips — plan output folder size accordingly.

### Negative prompt standard for Hunyuan

Hunyuan benefits from concise negatives. Suggested baseline:

```
"worst quality, low quality, blurry, jittery, deformed face, extra limbs, watermark, text"
```

Tune per-render based on the artifacts you actually see.

---

## Workflow Loading and Patching Pattern

### The Golden Rule

> **Load the workflow once. Deep copy. Patch only what changes per job. Base file never touched.**

```python
import copy, json, os

def load_workflow(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_flux_workflow(filename: str, prompt: str, seed: int,
                        output_dir: str, save_prefix: str,
                        base_workflow_path: str) -> dict:
    """
    Returns a fully patched deep copy of the base FLUX image edit workflow.
    Overrides: image filename, edit prompt, output path/prefix, seed.
    """
    wf = copy.deepcopy(load_workflow(base_workflow_path))

    wf["198"]["inputs"]["image"]              = filename         # Override 1: LoadImage
    wf["6"]["inputs"]["text"]                 = prompt           # Override 2: CLIPTextEncode
    wf["225"]["inputs"]["output_path"]        = output_dir       # Override 3: ttN imageOutput
    wf["225"]["inputs"]["save_prefix"]        = save_prefix
    wf["225"]["inputs"]["file_type"]          = "jpg"
    wf["225"]["inputs"]["overwrite_existing"] = False
    wf["225"]["inputs"]["embed_workflow"]     = True
    wf["225"]["inputs"]["image_output"]       = "Save"
    wf["225"]["inputs"]["number_padding"]     = 5
    wf["163"]["inputs"]["seed"]               = seed             # Optional: seed variation

    return wf

def build_flux_t2i_workflow(prompt: str, base_workflow_path: str) -> dict:
    """
    Returns a fully patched deep copy of the base FLUX 2 image-gen (T2I) workflow.
    Override: text prompt only (node 135). Output is whatever the workflow's
    SaveImage node writes -- usually ComfyUI's `output/Flux2_Klein_9b_kv/`.
    """
    wf = copy.deepcopy(load_workflow(base_workflow_path))
    wf["135"]["inputs"]["text"] = prompt
    return wf

def build_ltx_workflow(filename: str, prompt: str, filename_prefix: str,
                       t2v_mode: bool = False,
                       base_workflow_path: str = None) -> dict:
    """
    Returns a fully patched deep copy of the base LTX video workflow.
    Overrides: prompt text, source image, output path, I2V/T2V switch.
    """
    wf = copy.deepcopy(load_workflow(base_workflow_path))

    wf["267:266"]["inputs"]["value"]          = prompt           # Prompt text
    wf["269"]["inputs"]["image"]             = filename         # Source image filename
    wf["75"]["inputs"]["filename_prefix"]    = filename_prefix # Output path + stem
    wf["267:201"]["inputs"]["value"]          = t2v_mode        # False=I2V, True=T2V

    return wf

def build_hunyuan_t2v_workflow(
    prompt: str,
    negative_prompt: str,
    filename_prefix: str,
    frame_rate: int = 24,
    base_workflow_path: str = "",
) -> dict:
    """
    Returns a deep copy of a Hunyuan T2V workflow with the prompt,
    negative prompt, output filename prefix, and frame rate patched.
    Node IDs below are placeholders -- confirm from /object_info on the
    target install.
    """
    wf = copy.deepcopy(load_workflow(base_workflow_path))

    # Positive prompt
    wf["<CLIPTextEncode.pos>"]["inputs"]["text"] = prompt
    # Negative prompt
    wf["<CLIPTextEncode.neg>"]["inputs"]["text"] = negative_prompt
    # Output: filename_prefix and frame rate
    wf["<VHS_VideoCombine>"]["inputs"]["filename_prefix"] = filename_prefix
    wf["<VHS_VideoCombine>"]["inputs"]["frame_rate"]      = frame_rate

    return wf
```

---

## API Library — Reference Implementation

> **Production code:** A battle-tested, path-agnostic implementation is
> shipped at [scripts/api_lib.py](scripts/api_lib.py). It includes a
> persistent WebSocket with thread-safe reconnect, queue/history/interrupt
> helpers, and an env-var-configurable host. Prefer it (or copy the patterns
> from it) over the snippet below.

The class below is the inline reference, kept for environments that want
to embed the API helpers directly without depending on `scripts/api_lib.py`.

### Dependencies

```
pip install requests websocket-client
```

### Core class (inline fallback)

```python
import uuid, json, requests, websocket

class ComfyUI:
    def __init__(self, host: str = "http://127.0.0.1:8188",
                 ws_host: str = "ws://127.0.0.1:8188"):
        self.host = host
        self.ws   = ws_host

    def is_alive(self) -> bool:
        try:
            return requests.get(f"{self.host}/system_stats", timeout=5).status_code == 200
        except Exception:
            return False

    def object_info(self) -> dict:
        return requests.get(f"{self.host}/object_info", timeout=30).json()

    def get_node_class(self, node_name: str) -> dict | None:
        return self.object_info().get(node_name)

    def queue_prompt(self, workflow: dict, client_id: str) -> str:
        payload = {"prompt": workflow, "client_id": client_id}
        r = requests.post(f"{self.host}/prompt", json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(f"ComfyUI rejected workflow: {data['error']}")
        return data["prompt_id"]

    def wait_for_completion(self, prompt_id: str,
                            ws: websocket.WebSocket,
                            timeout: float = None) -> dict:
        start = time.time() if timeout else None
        while True:
            if timeout is not None and (time.time() - start) > timeout:
                raise TimeoutError(f"Job {prompt_id} did not complete within {timeout}s")
            raw = ws.recv()
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            if (msg.get("type") == "executing"
                    and msg.get("data", {}).get("node") is None
                    and msg.get("data", {}).get("prompt_id") == prompt_id):
                break
        resp = requests.get(f"{self.host}/history/{prompt_id}", timeout=10)
        history = resp.json()
        if prompt_id not in history:
            raise RuntimeError(f"Job {prompt_id} missing from /history after completion signal")
        job = history[prompt_id]
        if job.get("status", {}).get("status_str") == "error":
            raise RuntimeError(f"Job {prompt_id} errored -- check ComfyUI console")
        return job

    def get_history(self, prompt_id: str) -> dict:
        return requests.get(f"{self.host}/history/{prompt_id}", timeout=10).json()

    def get_queue(self) -> dict:
        return requests.get(f"{self.host}/queue", timeout=10).json()

    def interrupt(self) -> None:
        requests.post(f"{self.host}/interrupt", timeout=10)

    def clear_queue(self) -> None:
        requests.post(f"{self.host}/queue", json={"clear": True}, timeout=10)
```

### Usage pattern

```python
client = ComfyUI(host="http://127.0.0.1:8188")

# One-time setup per batch run
client_id = str(uuid.uuid4())
ws = websocket.WebSocket()
ws.connect(f"{client.ws}/ws?clientId={client_id}")

try:
    for image_path in images:
        filename = copy_to_comfyui_input(image_path, comfyui_input_dir)
        seed     = random.randint(0, 2**32 - 1)
        wf       = build_flux_workflow(filename, prompt, seed, output_dir, save_prefix, base_path)
        prompt_id = client.queue_prompt(wf, client_id)
        client.wait_for_completion(prompt_id, ws)
        print(f"OK: {image_path}")
finally:
    ws.close()
```

### Production vs. inline -- which to use

| Situation | Use |
|-----------|-----|
| Building a real batch runner, long-lived script, or agent tool | [scripts/api_lib.py](scripts/api_lib.py) (persistent WS, reconnect, env-var config) |
| Quick inline tests, throwaway scripts, learning examples | The `ComfyUI` class above |
| Embedded in a notebook where module imports are awkward | The `ComfyUI` class above |

The two implementations are behaviorally compatible -- you can swap between
them without changing call sites.

---

## Image Resolution Helpers

```python
from pathlib import Path

def derive_output_dir(input_folder: str, batch_index: int = None) -> str:
    """Auto-derives output directory from input folder name."""
    p = Path(input_folder)
    batch_root = p / f"{p.name} flux edit batch"
    if batch_index is not None:
        return str(batch_root / f"batch_{batch_index:02d}")
    return str(batch_root)

def derive_save_prefix(input_folder: str, batch_index: int = None) -> str:
    """Clean input folder name -> filesystem-safe save prefix."""
    import re
    name  = Path(input_folder).name
    clean = re.sub(r"[^\w\s]", "", name)
    clean = re.sub(r"\s+", "_", clean).lower().strip("_")
    if batch_index is not None:
        return f"{clean}_b{batch_index:02d}_"
    return f"{clean}_"

def derive_job_folder(input_folder: str, workflow_name: str,
                     batch_jobs_root: str) -> str:
    """Derives the job script folder in the project workspace."""
    import re
    def to_snake(s):
        s = re.sub(r"[^\w\s]", "", s)
        return re.sub(r"\s+", "_", s).lower().strip("_")
    folder_snake   = to_snake(Path(input_folder).name)
    workflow_snake = to_snake(workflow_name)
    return str(Path(batch_jobs_root) / f"{folder_snake}_batch_job_{workflow_snake}")

def derive_job_folder_dated(
    batch_jobs_root: str,
    project_name: str,
    batch_name: str,
    when: str | None = None,
) -> str:
    """
    Date-prefixed job folder, organized per project.

    Returns: `{batch_jobs_root}/{PROJECT_NAME}/{YYYY-MM-DD}_{batch_name}/`

    `when` is an ISO date string (YYYY-MM-DD); defaults to today.

    Use this when you want multiple runs of the same project to be grouped
    and to never overwrite each other.
    """
    from datetime import date
    import re
    when_iso = when or date.today().isoformat()
    safe = re.sub(r"[^\w\-]", "_", batch_name).lower()[:40]
    return str(Path(batch_jobs_root) / project_name / f"{when_iso}_{safe}")

def derive_temp_workflow_copy(
    temp_root: str,
    project_name: str,
    batch_name: str,
    workflow_filename: str,
    when: str | None = None,
) -> str:
    """
    Returns: `{temp_root}/{PROJECT_NAME}/{YYYY-MM-DD}_{batch_name}/{filename}.json`

    Copy the base workflow here before patching. Delete after the run.
    """
    from datetime import date
    import re
    when_iso = when or date.today().isoformat()
    safe = re.sub(r"[^\w\-]", "_", batch_name).lower()[:40]
    wf_clean = re.sub(r"[^\w]", "_", workflow_filename)
    return str(Path(temp_root) / project_name / f"{when_iso}_{safe}" / wf_clean)

def resolve_images(folder: str, extensions=None) -> list[str]:
    """Recursively find all image files in a folder."""
    if extensions is None:
        extensions = ["jpg", "jpeg", "png", "webp", "JPG", "JPEG", "PNG", "WEBP"]
    p = Path(folder)
    images = []
    for ext in extensions:
        images.extend(sorted(p.glob(f"**/*.{ext}"), key=lambda x: x.name))
    # Deduplicate by lowercase name
    seen, unique = set(), []
    for img in images:
        if img.name.lower() not in seen:
            seen.add(img.name.lower())
            unique.append(str(img))
    return unique
```

---

## Prompt Versioning for LLM-Generated Prompts

When generating prompts via LLM for batch runs, follow the non-destructive pipeline:

1. **JoyCaption** → raw scene descriptions → `captions.txt` (never modified)
2. **LLM reads prompting guide** → generates unique cinematic prompts
3. **Save to JSON** with versioning block:

```json
{
  "_version": {
    "v": 1,
    "description": "Initial cinematic pass — outdoor scenes, warm lighting",
    "date": "2026-04-01",
    "negative": "avoid locked-off static frame as sole camera behaviour, frozen motion, still photography, cartoonish"
  },
  "image_001.jpg": {
    "prompt": "The camera slowly tracks right as the subject walks forward...",
    "description": "Person walking on cobblestone street at golden hour"
  }
}
```

4. **Keep old versions** — never overwrite. Generate v2, v3 as style evolves.

### Negative Prompt Standard

Keep negatives **brief and targeted**. The model responds better to direction than negation.

```
Negative: "avoid locked-off static frame as sole camera behaviour, frozen motion, still photography, cartoonish"
```

Do NOT pile on synonyms — "static, still, frozen, motionless, no movement" etc. Let the positive prompt describe what SHOULD happen.