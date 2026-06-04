#!/usr/bin/env python3
"""
ComfyUI FLUX 2 Image Edit -- Batch Script Template
====================================================

A sanitized, path-agnostic starter script for running a FLUX 2 image-edit
batch against any ComfyUI install. Use this as a template -- copy into your
project, fill in the CONFIG section, and run.

Pattern: load once -> deep copy -> override nodes -> queue -> WebSocket
block -> /history verify -> repeat. Do not edit the base workflow file;
this script always deep-copies.

USAGE:
  1. Fill in CONFIG (see the block below)
  2. Run:  python3 run_batch.py
  3. Outputs land in {input_folder}/{folder_name} flux edit batch/

CONFIGURATION (priority order):
  1. CONFIG constants below
  2. Environment variables:
       COMFYUI_HOST         (default: http://127.0.0.1:8188)
       COMFYUI_WS           (default: ws://127.0.0.1:8188)
       COMFYUI_INPUT_DIR    (REQUIRED -- set to your install's input/ dir)

DEPENDENCIES:
  pip install requests websocket-client

OUTPUT FOLDER NAMING:
  {input_folder}/{input_folder_name} flux edit batch/[batch_XX/]
  Jobs land in {JOBS_ROOT}/{PROJECT_NAME}/{YYYY-MM-DD}_{batch_name}/
"""

import copy
import datetime
import json
import os
import random
import re
import shutil
import sys
import uuid
from pathlib import Path

# Add scripts/ to path so we can import api_lib.py
_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))
from api_lib import (  # type: ignore
    queue_prompt,
    wait_for_completion,
    load_workflow,
    reset_connection,
    comfyui_is_alive,
    DEFAULT_HOST,
    DEFAULT_WS,
)


# ══════════════════════════════════════════════════════════════════════════════
# CONFIG -- User fills this in
# ══════════════════════════════════════════════════════════════════════════════

# ComfyUI host (env var COMFYUI_HOST overrides)
COMFYUI_HOST = os.environ.get("COMFYUI_HOST", DEFAULT_HOST)
COMFYUI_WS   = os.environ.get("COMFYUI_WS",   DEFAULT_WS)

# ComfyUI's input/ directory -- where the workflow's LoadImage node will read from.
# REQUIRED: set this to your ComfyUI install's input/ folder.
# Examples:
#   Windows:  C:/path/to/ComfyUI/input
#   Linux:    /home/user/ComfyUI/input
#   macOS:    /Users/user/ComfyUI/input
COMFYUI_INPUT_DIR = os.environ.get("COMFYUI_INPUT_DIR", "")

# Base workflow JSON to load. Use a path the user supplies, never an absolute
# hardcoded path.
BASE_WORKFLOW_PATH = ""  # e.g. "workflows/Flux 2 Image edit workflow API/Flux 2 Image edit workflow API.json"

# Where generated batch jobs live. Created if missing.
JOBS_ROOT = ""  # e.g. "jobs"

# Optional: where patched workflow copies are staged during a run.
# Leave empty ("") to load the base workflow directly without staging.
TEMP_WORKFLOW_ROOT = ""  # e.g. "temp"

# Per-run variables
INPUT_FOLDER = ""  # source images
PROJECT_NAME = ""  # grouping folder (e.g. "MyProject", "Marketing_2026")
BATCH_NAME   = ""  # short description (e.g. "first_pass", "sunset_v2")

# The workflow "name" used for the temp copy and for any internal naming.
# If you leave it empty, it is derived from BASE_WORKFLOW_PATH basename.
WORKFLOW_FILENAME = ""

# One or more prompts -- each gets its own batch_NN/ subfolder.
BATCHES = [
    "make this photoreal, cinematic lighting, enhance atmospheric depth",
    # Add more prompts here for multi-batch runs.
]

# ══════════════════════════════════════════════════════════════════════════════
# FIXED DEFAULTS -- usually leave alone
# ══════════════════════════════════════════════════════════════════════════════

FILE_TYPE      = "jpg"
RANDOMIZE_SEED = True
JOB_TIMEOUT    = 600   # seconds per job
WORKFLOW_NAME  = "Flux 2 Image Edit"  # used only for job-folder naming


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def derive_output_dir(input_folder: str, batch_index: int | None = None) -> str:
    """{input_folder}/{folder_name} flux edit batch/[batch_XX/]"""
    p = Path(input_folder)
    batch_root = p / f"{p.name} flux edit batch"
    if batch_index is not None:
        return str(batch_root / f"batch_{batch_index:02d}")
    return str(batch_root)


def derive_save_prefix(input_folder: str, batch_index: int | None = None) -> str:
    """Filesystem-safe prefix derived from input folder name."""
    name = Path(input_folder).name
    clean = re.sub(r"[^\w\s]", "", name)
    clean = re.sub(r"\s+", "_", clean).lower().strip("_")
    if batch_index is not None:
        return f"{clean}_b{batch_index:02d}_"
    return f"{clean}_"


def derive_job_folder_dated(when: str | None = None) -> str:
    """{JOBS_ROOT}/{PROJECT_NAME}/{YYYY-MM-DD}_{batch_name}/"""
    today = when or datetime.date.today().isoformat()
    safe = re.sub(r"[^\w\-]", "_", BATCH_NAME).lower()[:40]
    return str(Path(JOBS_ROOT) / PROJECT_NAME / f"{today}_{safe}")


def derive_temp_workflow_copy(when: str | None = None) -> str:
    """{TEMP_WORKFLOW_ROOT}/{PROJECT_NAME}/{YYYY-MM-DD}_{batch_name}/{wf_name}.json"""
    if not TEMP_WORKFLOW_ROOT:
        return ""
    today = when or datetime.date.today().isoformat()
    safe = re.sub(r"[^\w\-]", "_", BATCH_NAME).lower()[:40]
    wf_clean = re.sub(r"[^\w]", "_", WORKFLOW_FILENAME)
    return str(Path(TEMP_WORKFLOW_ROOT) / PROJECT_NAME / f"{today}_{safe}" / wf_clean)


def resolve_images(folder: str) -> list[str]:
    """Recursively find image files, deduped by lowercase filename."""
    p = Path(folder)
    if not p.exists():
        raise FileNotFoundError(f"Input folder not found: {folder}")
    images = []
    for ext in ("jpg", "jpeg", "png", "webp", "JPG", "JPEG", "PNG", "WEBP"):
        images.extend(sorted(p.glob(f"**/*.{ext}"), key=lambda x: x.name))
    seen, unique = set(), []
    for img in images:
        if img.name.lower() not in seen:
            seen.add(img.name.lower())
            unique.append(str(img))
    return unique


def copy_to_comfyui_input(image_path: str) -> str:
    """Copy image to ComfyUI input/ and return the filename only."""
    if not COMFYUI_INPUT_DIR:
        raise RuntimeError(
            "COMFYUI_INPUT_DIR is not set. "
            "Set it in the CONFIG block or via the COMFYUI_INPUT_DIR env var."
        )
    filename = os.path.basename(image_path)
    shutil.copy2(image_path, os.path.join(COMFYUI_INPUT_DIR, filename))
    return filename


def get_workflow_copy() -> dict:
    """Load the workflow, optionally staging a temp copy first."""
    if TEMP_WORKFLOW_ROOT and WORKFLOW_FILENAME:
        temp_path = derive_temp_workflow_copy()
        if temp_path:
            temp_file = Path(temp_path)
            if not temp_file.exists():
                temp_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(BASE_WORKFLOW_PATH, temp_path)
            return load_workflow(temp_path)
    return load_workflow(BASE_WORKFLOW_PATH)


def cleanup_temp_workflow() -> None:
    """Delete the temp workflow copy after the run."""
    if not (TEMP_WORKFLOW_ROOT and WORKFLOW_FILENAME):
        return
    temp_path = derive_temp_workflow_copy()
    if not temp_path:
        return
    p = Path(temp_path)
    if p.exists():
        p.unlink()
        for parent in p.parents:
            try:
                parent.rmdir()
            except OSError:
                break


def build_workflow(filename: str, prompt: str, seed: int,
                   output_dir: str, save_prefix: str) -> dict:
    """Deep-copy base workflow, override 3 nodes + seed. Base file untouched."""
    wf = copy.deepcopy(get_workflow_copy())
    wf["198"]["inputs"]["image"]              = filename   # LoadImage
    wf["6"]["inputs"]["text"]                 = prompt     # CLIPTextEncode
    wf["225"]["inputs"]["output_path"]        = output_dir # ttN imageOutput
    wf["225"]["inputs"]["save_prefix"]        = save_prefix
    wf["225"]["inputs"]["file_type"]          = FILE_TYPE
    wf["225"]["inputs"]["overwrite_existing"] = False
    wf["225"]["inputs"]["embed_workflow"]     = True
    wf["225"]["inputs"]["image_output"]       = "Save"
    wf["225"]["inputs"]["number_padding"]     = 5
    wf["163"]["inputs"]["seed"]               = seed       # KSampler seed
    return wf


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> int:
    # -- Validate CONFIG --------------------------------------------------
    missing = []
    if not BASE_WORKFLOW_PATH: missing.append("BASE_WORKFLOW_PATH")
    if not JOBS_ROOT:          missing.append("JOBS_ROOT")
    if not INPUT_FOLDER:       missing.append("INPUT_FOLDER")
    if not PROJECT_NAME:       missing.append("PROJECT_NAME")
    if not BATCH_NAME:         missing.append("BATCH_NAME")
    if not COMFYUI_INPUT_DIR:  missing.append("COMFYUI_INPUT_DIR")
    if missing:
        raise SystemExit(
            "Missing CONFIG values: "
            + ", ".join(missing)
            + "\nFill them in or set the corresponding environment variables."
        )

    # Derive workflow display name from the path if not set
    global WORKFLOW_FILENAME
    if not WORKFLOW_FILENAME:
        WORKFLOW_FILENAME = Path(BASE_WORKFLOW_PATH).stem

    # -- Pre-flight -------------------------------------------------------
    if not comfyui_is_alive(COMFYUI_HOST):
        raise SystemExit(f"ComfyUI not running at {COMFYUI_HOST}. Start it first.")

    if not Path(BASE_WORKFLOW_PATH).exists():
        raise SystemExit(f"Base workflow not found: {BASE_WORKFLOW_PATH}")

    images = resolve_images(INPUT_FOLDER)
    if not images:
        raise SystemExit(f"No images found in: {INPUT_FOLDER}")

    multi = len(BATCHES) > 1
    expected_total = len(images) * len(BATCHES)

    # -- Job folder -------------------------------------------------------
    job_folder = derive_job_folder_dated()
    os.makedirs(job_folder, exist_ok=True)

    # -- Save batch_config.json -------------------------------------------
    with open(os.path.join(job_folder, "batch_config.json"), "w", encoding="utf-8") as f:
        json.dump({
            "input_folder":     INPUT_FOLDER,
            "batches":          BATCHES,
            "output_dirs":      [derive_output_dir(INPUT_FOLDER, i + 1 if multi else None)
                                 for i in range(len(BATCHES))],
            "workflow_file":    WORKFLOW_FILENAME,
            "job_folder":       job_folder,
            "project_name":     PROJECT_NAME,
            "batch_name":       BATCH_NAME,
            "expected_outputs": expected_total,
            "comfyui_host":     COMFYUI_HOST,
            "generated_at":     datetime.datetime.now().isoformat(),
        }, f, indent=2)

    print("=" * 54)
    print("  FLUX 2 Image Edit Batch")
    print(f"  Project:  {PROJECT_NAME}")
    print(f"  Batch:    {BATCH_NAME}")
    print(f"  Input:    {INPUT_FOLDER}")
    print(f"  Images:   {len(images)}")
    print(f"  Batches:  {len(BATCHES)}")
    print(f"  Expected: {expected_total} output files")
    print(f"  Job dir:  {job_folder}")
    print("=" * 54)
    print()

    all_results = []
    success_count = 0

    # -- Run loop: one client_id, one WS, block per job --------------------
    client_id = str(uuid.uuid4())
    ws = None

    try:
        import websocket  # type: ignore
        ws = websocket.WebSocket()
        ws.connect(f"{COMFYUI_WS.rstrip('/')}/ws?clientId={client_id}")

        for b_idx, prompt in enumerate(BATCHES, start=1):
            output_dir  = derive_output_dir(INPUT_FOLDER, b_idx if multi else None)
            save_prefix = derive_save_prefix(INPUT_FOLDER, b_idx if multi else None)
            os.makedirs(output_dir, exist_ok=True)
            batch_results = []

            print(f"Batch {b_idx}/{len(BATCHES)}: \"{prompt[:72]}\"")
            print(f"  Output -> {output_dir}")
            print()

            for i, image_path in enumerate(images, start=1):
                label = os.path.basename(image_path)
                print(f"  [{i:>3}/{len(images)}] {label}", end="  ", flush=True)

                if not os.path.exists(image_path):
                    print("SKIP (file missing)")
                    batch_results.append({"file": label, "status": "skipped"})
                    continue

                try:
                    filename  = copy_to_comfyui_input(image_path)
                    seed      = random.randint(0, 2**32 - 1) if RANDOMIZE_SEED else 0
                    wf        = build_workflow(filename, prompt, seed, output_dir, save_prefix)
                    prompt_id = queue_prompt(wf, host=COMFYUI_HOST, client_id=client_id)
                    wait_for_completion(
                        prompt_id, ws=ws, host=COMFYUI_HOST, ws_host=COMFYUI_WS,
                        timeout=JOB_TIMEOUT,
                    )
                    print("OK")
                    batch_results.append({"file": label, "status": "success"})
                    success_count += 1
                except Exception as e:
                    print(f"FAIL  ({e})")
                    batch_results.append({"file": label, "status": f"error: {e}"})

            ok   = sum(1 for r in batch_results if r["status"] == "success")
            fail = sum(1 for r in batch_results if "error" in r["status"])
            skip = sum(1 for r in batch_results if r["status"] == "skipped")
            print()
            print(f"  Batch {b_idx} complete -- OK {ok}  FAIL {fail}  SKIP {skip}")
            print()
            all_results.append({"batch": b_idx, "prompt": prompt,
                                "results": batch_results, "output": output_dir})

    finally:
        if ws is not None:
            try:
                ws.close()
            except Exception:
                pass
        reset_connection()
        cleanup_temp_workflow()

    # -- Summary -----------------------------------------------------------
    print("=" * 54)
    print("  ALL BATCHES COMPLETE")
    print("=" * 54)
    for r in all_results:
        ok = sum(1 for x in r["results"] if x["status"] == "success")
        print(f"  Batch {r['batch']}: {ok}/{len(images)} OK  ->  {r['output']}")

    print()
    print(f"  Output verification: {success_count}/{expected_total}")
    if success_count != expected_total:
        print(f"  COUNT MISMATCH -- expected {expected_total}, got {success_count}")
        return 1
    print(f"  COUNT VERIFIED -- all {expected_total} outputs accounted for")
    print()
    print(f"  Job files -> {job_folder}")
    print(f"        run_{PROJECT_NAME}_{BATCH_NAME}.py")
    print(f"        batch_config.json")
    print("=" * 54)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
