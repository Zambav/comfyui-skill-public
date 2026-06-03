# Batch Operations Guide

> Portable patterns for running large ComfyUI batch jobs reliably — queue management, state tracking, recovery, and monitoring.

---

## Core Pattern: Queue-and-Watch

**The proven pattern: one client_id, one WebSocket, block on completion per job, verify with `/history`.**

This is why batch jobs succeed. Fire-and-forget POST calls without blocking are the primary cause of reliability failures.

### The Rule

> Load the workflow once. Override only the nodes that change per job. Block on WebSocket. Verify with `/history`. Repeat.

### Why Blocking Matters

Submitting all jobs at once (fire-and-forget) creates ambiguity about individual job fate. ComfyUI's queue is a shared buffer — jobs from other sessions can slip in. The only reliable done-signal is:

1. WebSocket receives `{"type": "executing", "data": {"node": null, "prompt_id": "<id>"}}`
2. Immediately confirmed with `GET /history/<prompt_id>`

### Recommended Pattern

```python
import uuid, json, requests, websocket

client_id = str(uuid.uuid4())
ws = websocket.WebSocket()
ws.connect(f"ws://{host}/ws?clientId={client_id}")

try:
    for job in jobs:
        workflow = build_workflow(job)           # patch only what changes
        prompt_id = queue_prompt(workflow, client_id)
        wait_for_completion(prompt_id, ws)       # block until done
        verify_with_history(prompt_id)            # confirm outputs exist
finally:
    ws.close()
```

One WebSocket connection is reused for the entire batch run. One `client_id` is reused for all jobs in that run.

---

## State File Pattern

For jobs that span sessions (long-running batches, overnight runs, or recovery scenarios), track state in a JSON file. This enables:

- Resume after interruption
- Watchdog recovery
- Progress reporting without re-querying ComfyUI

> **Storage location:** the state file is written inside the same job folder
> the run script lives in. That folder is created with
> `os.makedirs(job_folder, exist_ok=True)` before writing anything, and is
> never reused for a different run.

### Job State File

Save as `job_state.json` alongside the generated script:

```json
{
  "batch_name": "earth_maze_v2",
  "input_folder": "/path/to/your/earth_maze",
  "workflow_file": "Flux 2 Image edit workflow API.json",
  "created_at": "2026-04-01T03:00:00Z",
  "jobs": [
    {
      "label": "earth_maze_00001.jpg",
      "image_path": "/path/to/your/earth_maze/earth_maze_00001.jpg",
      "batch_prompt": "enhance realism, cinematic lighting",
      "seed": 1234567890,
      "output_dir": "/path/to/your/earth_maze/earth_maze flux edit batch/batch_01",
      "save_prefix": "earth_maze_",
      "status": "success",
      "prompt_id": "abc123",
      "submitted_at": "2026-04-01T03:00:05Z",
      "completed_at": "2026-04-01T03:01:12Z",
      "error": null
    }
  ]
}
```

### Status Values

| Status | Meaning |
|---|---|
| `pending` | Not yet submitted |
| `submitted` | Queued to ComfyUI, awaiting completion |
| `success` | Completed with outputs verified |
| `failed` | Completed but outputs missing or error in history |
| `timeout` | Exceeded `JOB_TIMEOUT` seconds |

### Resume Logic

```python
# Skip jobs already marked success
for job in jobs:
    if job["status"] == "success":
        continue
    # ... submit and update status
```

---

## Watchdog / Recovery Pattern

A stateless watchdog script can recover a stalled batch without knowing anything about the workflow:

1. Read `job_state.json`
2. For each job marked `submitted`: check `GET /history/<prompt_id>`
   - If present and successful → mark `success`
   - If present and error → mark `failed`
3. For jobs stuck `submitted` beyond `JOB_TIMEOUT`: resubmit
4. If queue is dry but `submitted` jobs remain: interrupt, clear, resubmit

### Exit Codes

| Code | Meaning |
|---|---|
| `0` | Healthy — nothing to do |
| `1` | Recovered — stalled jobs restarted (announce to user) |
| `2` | ComfyUI is down |
| `3` | No batch found (no `job_state.json` in expected location) |

### Recovery Triggers

- Job in `submitted` state for more than `JOB_TIMEOUT` seconds
- Queue empty but `submitted` jobs still pending
- ComfyUI was restarted mid-batch

### Batch Monitoring

For cron job setup, Discord notifications, error recovery, and monitoring SOP — see **[`cron-jobs.md`](./cron-jobs.md)**.

Key rules:
- Only one ComfyUI batch cron may exist at a time — destroy old before creating new
- Ask the user for a Discord channel ID to use for progress notifications at batch startup
- Create cron when first image returns OK and batch is confirmed running
- For destroy rules and recovery policy, follow `cron-jobs.md` as the source of truth

---

## Output Folder Naming Convention

Output folders are always **relative to the input folder** and self-describing:

```
{input_folder}/{input_folder_name} flux edit batch/
    batch_01/    <- batch 1 outputs
    batch_02/    <- batch 2 outputs (if multiple prompts)
```

```
# Formula (replace with your actual paths)
input_folder = "/path/to/your/portraits"
batch_root   = "/path/to/your/portraits/portraits flux edit batch"
batch_01     = "/path/to/your/portraits/portraits flux edit batch/batch_01"
```

This keeps source images and outputs together. No hunting across the filesystem.

---

## Job Folder Structure

All generated scripts, logs, and state for a batch run live in a **job folder** inside the project workspace -- never inside the input or output image folders.

```
{project_root}/jobs/
    {input_folder_name}_batch_job_{workflow_name_snake_case}/
        run_batch.py          # the generated batch script
        job_state.json         # live state file (created at run time)
        batch_config.json      # snapshot of run parameters
```

If you want runs grouped by project (one project, many batches over time),
use a date-prefixed layout -- see
[`derive_job_folder_dated`](./reference-implementations.md#image-resolution-helpers):

```
{project_root}/jobs/
    {PROJECT_NAME}/
        {YYYY-MM-DD}_{short_description}/
            run_{PROJECT}_{BATCH}.py
            job_state.json
            batch_config.json
```

This is the recommended layout for production: it groups related runs under
a project name and uses a date prefix so runs never overwrite each other.

**Examples (replace with your actual paths):**

| Input folder | Workflow | Job folder |
|---|---|---|
| `/photos/portraits` | `Flux 2 Image edit workflow API` | `jobs/portraits_batch_job_flux_2_image_edit_workflow_api/` |
| `/renders/scifi` | `LTX 2.3 Video I2V_T2V` | `jobs/scifi_batch_job_ltx_2_3_video_i2v_t2v/` |
| `/photos/portraits` (re-run on 2026-05-22) | `Flux 2 Image edit workflow API` | `jobs/MyProject/2026-05-22_second_pass/` (dated layout) |

---

## Batch Script Template

A generated batch script should contain:

1. **Config section** -- `INPUT_FOLDER`, `BATCHES`, `JOBS_ROOT` (all
   supplied by the user or derived, never hardcoded in the template)
2. **Helpers** -- `derive_output_dir`, `derive_save_prefix`,
   `derive_job_folder` (and `derive_job_folder_dated` for production),
   `resolve_images`
3. **Pre-flight checks** -- ComfyUI alive, workflow file exists, images
   found, input dir accessible
4. **Main loop** -- one client_id, one WS, block per job, verify
5. **Summary** -- success/fail counts, output paths, count verification

A working, sanitized starter is at [`scripts/template_run_batch.py`](./scripts/template_run_batch.py).
It reads the workflow from a user-supplied path, uses an env-var-configurable
ComfyUI host, and derives the output / job folders from the input folder.
Copy it into your project, fill in the `CONFIG` block, and run.

The script is **generated per run** and **never edits the base workflow file**.

---

## Multi-Batch Runs

When running multiple batches (different prompts over the same images):

1. Each prompt gets its own `batch_NN/` subfolder
2. Each job in `job_state.json` records which batch it belongs to
3. All batches share the same `client_id` and WebSocket for the run
4. `job_state.json` is written once at start, updated after each job completes

---

## Python Invocation

On systems where `python` is not in PATH, use the appropriate launcher:

```bash
# Windows (if python not in PATH)
py -3 run_batch.py

# Linux/macOS
python3 run_batch.py
```

Always verify the ComfyUI input directory path matches the target machine before running.

---

## Batch Monitoring & Cron Jobs

For all cron job setup, monitoring SOP, Discord message formats, error recovery rules, and progress field definitions — see **[`cron-jobs.md`](./cron-jobs.md)**.

This includes:
- Discord message templates (start ping, progress ping, completion ping, failure ping)
- Progress ping field definitions (done, avg_time, eta, iph, errors, longest, shortest)
- Cron setup procedure (ask for Discord channel first, check/destroy old, create after first successful render confirms batch is running)
- Error recovery sequence (assess → fix → report → retry, max 3 attempts)
- Cron destroy rules (success, failed, stalled, new batch, manual override)

---

## Assumptions You Must Never Make

- Do not assume `127.0.0.1:8188` is the only target -- accept base URL as a parameter (or env var `COMFYUI_HOST`)
- Do not assume a particular input directory layout -- discover or confirm
  input/output paths from the user
- Do not assume the workflow file is at a specific absolute path -- let the
  user supply it (or discover it from a user-owned `workflows/` folder)
- Do not assume model filenames -- always confirm from `/object_info` or
  user config
- Do not assume a Discord channel ID, bot token, or any notification
  destination -- ask the user at batch startup

---

## Intake Questionnaire (for an agent running a batch)

When a user asks the agent to run a batch (image edit, video, etc.), ask only
the questions needed to fill the script's CONFIG block. Do not guess.

For an image edit / batch job:

1. **"Where are the photos / what's the input folder?"** -- input path
2. **"Where should outputs go?"** -- output path, or accept the auto-derived
   `{input_folder}/{input_folder_name} flux edit batch/`
3. **"What should I call this batch?"** -- short description for the job folder
4. **"What's the prompt?"** -- edit instruction (I2I) or description (T2I)
5. **"One batch, or multiple batches with different prompts?"**

For LTX / WAN / Hunyuan video:

6. **"Image-to-video or text-to-video?"** -- if I2V, also ask for source image
7. **"What should I call the output file?"** -- used as `filename_prefix`
   (make it project-specific to avoid overwriting)

For monitoring:

8. **"Where should I post progress updates?"** -- collect a destination from
   the user at batch startup. Do not hardcode this.

**Before running:** check for existing `joycaption.md` in the input folder
(see [`docs/joycaption-convention.md`](./docs/joycaption-convention.md)).
If found, ask the user: "Found existing `joycaption.md` -- use it, update
it, or start fresh?"
