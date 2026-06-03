"""
comfyui-skill-public — ComfyUI API helpers
==========================================

Battle-tested, path-agnostic helpers for talking to a ComfyUI instance.

This module is the production-quality version of the patterns documented in
`reference-implementations.md`. Use it directly, copy it into your project,
or import the patterns into your own helpers.

Configuration (in priority order):
  1. Function arguments (host, ws_host)  -- always wins
  2. Environment variables:
       COMFYUI_HOST   -- e.g. http://127.0.0.1:8188  (default)
       COMFYUI_WS     -- e.g. ws://127.0.0.1:8188    (default)
  3. Built-in defaults (loopback 127.0.0.1:8188)

Dependencies:
  pip install requests websocket-client

Design principles:
  * One persistent WebSocket per process, reused across many jobs.
  * Thread-safe WS reconnect via a lock; auto-reconnect on transport errors.
  * Blocking completion detection via the official "executing" with
    node=None message; verified with GET /history/{prompt_id}.
  * Defensive parsing of /history (schema varies by ComfyUI version).

This file contains NO machine-specific paths, NO personal data, and NO
workflow specifics -- it is safe to commit and to share.
"""

import json
import os
import pathlib
import threading
import time
import uuid
from typing import Any, Iterable

import requests
import websocket  # type: ignore
import websocket._exceptions as ws_exceptions  # type: ignore


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_HOST = os.environ.get("COMFYUI_HOST", "http://127.0.0.1:8188")
DEFAULT_WS = os.environ.get("COMFYUI_WS", "ws://127.0.0.1:8188")


def _normalize_host(host: str) -> str:
    """Strip trailing slash, accept either 'host:port' or 'http(s)://host:port'."""
    host = host.rstrip("/")
    if not host.startswith(("http://", "https://", "ws://", "wss://")):
        host = "http://" + host
    return host


def _normalize_ws(ws: str) -> str:
    ws = ws.rstrip("/")
    if not ws.startswith(("ws://", "wss://")):
        ws = "ws://" + ws
    return ws


# ---------------------------------------------------------------------------
# Persistent WebSocket — one client_id, one WS, reused across jobs
# ---------------------------------------------------------------------------

_client_id: str | None = None
_ws: websocket.WebSocket | None = None
_ws_lock = threading.Lock()


def _get_client_id() -> str:
    """Return a stable client_id for this process (UUID4)."""
    global _client_id
    if _client_id is None:
        _client_id = str(uuid.uuid4())
    return _client_id


def _ws_url(ws_host: str) -> str:
    return f"{_normalize_ws(ws_host)}/ws?clientId={_get_client_id()}"


def _get_ws(ws_host: str = DEFAULT_WS) -> websocket.WebSocket:
    """Return the persistent WS, opening or reconnecting if needed."""
    global _ws
    with _ws_lock:
        if _ws is None or _ws.connected is False:
            _ws = websocket.create_connection(_ws_url(ws_host))
        return _ws


def reset_connection() -> None:
    """Force-close the persistent WS. Call between batch runs or after a transport error."""
    global _ws
    with _ws_lock:
        if _ws is not None:
            try:
                _ws.close()
            except Exception:
                pass
            _ws = None


# ---------------------------------------------------------------------------
# Core API helpers (host-aware; do not bake in the persistent WS)
# ---------------------------------------------------------------------------

def load_workflow(path: str | os.PathLike) -> dict:
    """Load a workflow JSON file. Caller is responsible for path resolution."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def queue_prompt(
    workflow: dict,
    host: str = DEFAULT_HOST,
    client_id: str | None = None,
) -> str:
    """
    POST a workflow to /prompt. Returns the prompt_id.
    Raises RuntimeError if ComfyUI rejects the workflow.
    """
    if client_id is None:
        client_id = _get_client_id()
    payload = {"prompt": workflow, "client_id": client_id}
    r = requests.post(
        f"{_normalize_host(host)}/prompt",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"ComfyUI rejected workflow: {data['error']}")
    return data["prompt_id"]


def wait_for_completion(
    prompt_id: str,
    ws: websocket.WebSocket | None = None,
    host: str = DEFAULT_HOST,
    ws_host: str = DEFAULT_WS,
    timeout: float | None = 600,
) -> dict:
    """
    Block on the WebSocket until ComfyUI signals this prompt_id is done,
    then verify via /history and return the history entry.

    If `ws` is None, the module-level persistent WS is used.

    Raises TimeoutError on timeout, RuntimeError on job error.
    """
    if ws is None:
        ws = _get_ws(ws_host)

    start = time.time()
    while True:
        if timeout is not None and (time.time() - start) > timeout:
            raise TimeoutError(
                f"Job {prompt_id} did not complete within {timeout}s"
            )

        try:
            msg = ws.recv()
        except ws_exceptions.WebSocketTimeoutException:
            continue
        except Exception:
            # Transport error -- try to reconnect once and continue
            reset_connection()
            ws = _get_ws(ws_host)
            continue

        if not isinstance(msg, str):
            continue
        try:
            data = json.loads(msg)
        except Exception:
            continue

        if data.get("type") == "executing":
            node_data = data.get("data", {})
            if (
                node_data.get("node") is None
                and node_data.get("prompt_id") == prompt_id
            ):
                break  # Done

        if data.get("type") == "execution_error":
            raise RuntimeError(
                f"Execution error for {prompt_id}: {data.get('data')}"
            )

    # Verify via /history
    resp = requests.get(
        f"{_normalize_host(host)}/history/{prompt_id}", timeout=10
    )
    resp.raise_for_status()
    history = resp.json()
    if prompt_id not in history:
        raise RuntimeError(
            f"Job {prompt_id} missing from /history after completion signal"
        )

    job = history[prompt_id]
    status_str = job.get("status", {}).get("status_str", "unknown")
    if status_str == "error":
        errors = job.get("status", {}).get("errors", [])
        raise RuntimeError(f"Job {prompt_id} errored: {errors}")
    return job


# ---------------------------------------------------------------------------
# Convenience queries
# ---------------------------------------------------------------------------

def get_history(
    prompt_ids: Iterable[str] | None = None,
    host: str = DEFAULT_HOST,
    max_entries: int = 100,
) -> dict:
    """Fetch /history. If prompt_ids given, filter to those IDs only."""
    params = {"max_entries": max_entries}
    r = requests.get(
        f"{_normalize_host(host)}/history", params=params, timeout=10
    )
    r.raise_for_status()
    history = r.json()
    if prompt_ids is not None:
        wanted = set(prompt_ids)
        return {pid: entry for pid, entry in history.items() if pid in wanted}
    return history


def comfyui_is_alive(host: str = DEFAULT_HOST) -> bool:
    """True if /system_stats returns 200 within 5s."""
    try:
        return (
            requests.get(f"{_normalize_host(host)}/system_stats", timeout=5).status_code
            == 200
        )
    except Exception:
        return False


def get_object_info(host: str = DEFAULT_HOST) -> dict:
    """Return /object_info as a dict. Used to discover available node classes and dropdown values."""
    r = requests.get(f"{_normalize_host(host)}/object_info", timeout=30)
    r.raise_for_status()
    return r.json()


def get_queue_info(host: str = DEFAULT_HOST) -> dict | None:
    """Return {"running": N, "queued": M} from /queue, or None on failure."""
    try:
        r = requests.get(f"{_normalize_host(host)}/queue", timeout=5)
        if r.status_code == 200:
            data = r.json()
            return {
                "running": len(data.get("queue_running", [])),
                "queued": len(data.get("queue_pending", [])),
            }
    except Exception:
        pass
    return None


def interrupt_queue(host: str = DEFAULT_HOST) -> bool:
    """POST /interrupt -- stops the currently running node(s)."""
    try:
        return (
            requests.post(f"{_normalize_host(host)}/interrupt", timeout=5).status_code
            == 200
        )
    except Exception:
        return False


def clear_queue(host: str = DEFAULT_HOST) -> bool:
    """POST /queue/clear -- removes all pending items from the queue."""
    try:
        return (
            requests.post(f"{_normalize_host(host)}/queue/clear", timeout=5).status_code
            == 200
        )
    except Exception:
        return False


def free_memory(
    host: str = DEFAULT_HOST,
    unload_models: bool = True,
    free_memory: bool = True,
) -> bool:
    """POST /free -- ask ComfyUI to release VRAM."""
    try:
        payload = {"unload_models": unload_models, "free_memory": free_memory}
        r = requests.post(
            f"{_normalize_host(host)}/free",
            json=payload,
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


def download_image(
    filename: str,
    subfolder: str = "",
    folder_type: str = "output",
    out_dir: str | os.PathLike = ".",
    host: str = DEFAULT_HOST,
) -> pathlib.Path:
    """GET /view?<filename>&subfolder&type and write the file under out_dir. Returns the path."""
    params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    r = requests.get(f"{_normalize_host(host)}/view", params=params)
    r.raise_for_status()
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    out_path.write_bytes(r.content)
    return out_path


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Smoke test -- does not submit a workflow, just checks connectivity.
    print(f"COMFYUI_HOST = {DEFAULT_HOST}")
    print(f"COMFYUI_WS   = {DEFAULT_WS}")
    print(f"alive: {comfyui_is_alive()}")
    info = get_object_info() if comfyui_is_alive() else {}
    print(f"object_info node classes: {len(info)}")
