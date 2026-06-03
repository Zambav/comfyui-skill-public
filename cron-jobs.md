# Batch Monitoring & Cron Jobs

> How to set up, operate, and recover a ComfyUI batch monitoring cron job — Discord notifications, progress tracking, and error recovery.

---

## Overview

Every long-running ComfyUI batch job gets a cron monitor. The cron checks the batch's progress every 30 minutes and reports to Discord. It can also attempt recovery if something breaks.

**Rules:**
- Only one ComfyUI batch cron may exist at a time. Always check `openclaw cron list` and destroy any existing cron before creating a new one.
- Always ask the user for a Discord channel ID to use for progress notifications before creating the cron. Do not hardcode channel IDs — collect this at batch startup.
- Create the cron after the first image/job returns OK and the batch is confirmed running.
- Cron is observe-and-report by default; it attempts recovery automatically (see Error Recovery below).

---

## Discord Message Format

### Start Ping (sent immediately when cron is created)

```
Started {job_name} — {N} images x {B} pass(es) | Output: {output_path} | ETA: ~{eta}
```

### Progress Ping (every 30 min while batch runs)

```
{batch_name} — Progress Update
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Renders complete:  {done} / {total}  ({pct}%)
Avg time/render:   {avg_time}
Est. completion:   {eta}
Images/hour:       {iph}
Latest output:      {latest_file}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Errors:            {errors}
Longest render:    {longest}
Shortest render:   {shortest}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Completion Ping (sent when all passes done)

```
{batch_name} — COMPLETE
{done}/{total} succeeded | Output: {output_path}
```

### Failure Ping (after 3 recovery attempts exhausted)

```
{batch_name} — FAILED
{done}/{total} completed before failure | Output: {output_path}
Problem: {what went wrong}
Fix attempted: {what was tried}
```

---

## Progress Ping Field Definitions

| Field | How to derive |
|---|---|
| `done` | Count files in output folder matching the batch's naming pattern (e.g. `*_<style>__*.jpg`) |
| `total` | `images × passes` for this batch |
| `pct` | `done / total × 100`, formatted as integer |
| `avg_time` | Total elapsed time / number of completed renders |
| `eta` | `(total - done) / iph` — only shown once iph is known |
| `iph` | `done / elapsed_hours` — images per hour since batch started |
| `latest_file` | Most recently modified output file in the batch folder |
| `errors` | Count of renders with `FAIL` status in job log or `error` status in ComfyUI `/history` |
| `longest` | Longest individual render time from ComfyUI `/history` for this batch |
| `shortest` | Shortest individual render time from ComfyUI `/history` for this batch |

---

## Cron Setup Procedure

> **OpenClaw / `openclaw cron` is one possible scheduler.** This skill is
> scheduler-agnostic -- the SOP works with any agent scheduler that can
> invoke a periodic prompt or run a script. Substitute the `openclaw cron`
> commands below with your scheduler's equivalent (cron, launchd, systemd
> timers, GitHub Actions, a Discord bot loop, etc.). The structure of the
> steps is the same.

### Step 1 -- Ask the user for a notification destination

Before creating the monitor, ask the user:

> "Where should I post batch progress updates?"

Collect whatever they answer (Discord channel ID, email, log file path,
webhook URL, etc.). The user owns this choice -- the skill does not assume
any default. Pass it through to the scheduler and the message templates.

### Step 2 -- Check for existing monitor

```bash
# OpenClaw example
openclaw cron list
# Linux cron
crontab -l | grep -i comfy
# systemd
systemctl --user list-timers
```

If one exists, destroy it:

```bash
openclaw cron delete {id}
# or
crontab -e   # then remove the line
```

### Step 3 -- Create the monitor (after the first successful render confirms the batch is running)

The cron / scheduled task should:

- Run at a fixed interval (30 minutes is a good default)
- Invoke an isolated context (so it does not collide with the main session)
- Pass through the notification destination and the job's output path
- Have a generous timeout (60s+ to gather stats and report)
- **Wait for the first successful render before creating it** -- never create
  a monitor for a batch that has not yet produced any output

```bash
# OpenClaw example -- substitute your scheduler's equivalent
openclaw cron add \
  --name "ComfyUI Batch Monitor -- {job_name}" \
  --every "30m" \
  --message "Check {batch_name} status: {output_path} -- count outputs and check for errors" \
  --announce --to "{notification_destination}" --channel "{channel_type}" \
  --session "isolated" --timeout-seconds 60
```

**Parameters:**

- `30m` interval -- checks every 30 minutes
- `announce` -- sends monitor output to the destination automatically
- `to` -- the destination collected from the user in Step 1
- `isolated` session -- monitor runs in its own context, does not affect main session
- `timeout-seconds 60` -- gives the monitor up to 60s to gather stats and report

### Step 4 -- Send start notification manually

The monitor won't fire immediately. Send the start notification right after
creating it -- see Start notification template above.

---

## Error Recovery

When the monitor detects a problem, it follows this sequence:

### Attempt sequence (max 3 recoveries per batch)

**On each error detected:**

1. **Assess** -- identify what went wrong (ComfyUI down, queue stalled,
   specific job failing, disk full, etc.)
2. **Fix** -- apply the minimum necessary fix:
   - ComfyUI down -> restart ComfyUI, wait for port 8188 to be listening again
   - Queue stalled -> `POST /interrupt` -> clear queue -> resubmit failed jobs
   - WebSocket drop -> recreate the connection (re-call `ws.connect()` or
     the equivalent in your helper module)
   - Individual render consistently failing -> log the image/prompt combo,
     skip it, continue
   - Disk near full -> pause and alert immediately
3. **Report** -- post to the destination the user gave: what the problem
   was, what was done to fix it, what happens next
4. **Retry** -- allow the batch to continue from where it left off

**After 3 recovery attempts:** Stop trying. Post final failure report to
the destination and destroy the monitor. Do not keep retrying indefinitely.

### Common recovery scenarios

| Problem | Fix |
|---------|-----|
| ComfyUI unreachable (`ERR_CONNECTION_REFUSED`) | Restart ComfyUI, wait for port 8188 to be listening again |
| Queue stalled, no progress >30 min | `POST /interrupt` then `POST /queue` with `{"clear": true}`. Re-run the batch script to resume from last successful output |
| WebSocket drops | Recreate the connection, resume |
| Individual render failing repeatedly | Skip that image, log it in `batch_config.json` under `skipped_images`, continue batch |
| Disk full | Pause immediately, alert the destination, do not continue |
| Batch silently producing no new outputs for >60 min | Treat as stalled -- attempt queue reset. Fail after 2 more attempts |

---

## Cron Destroy Rules

Destroy the cron and stop the batch when any of these conditions occur:

| Priority | Condition | Action |
|---|---|---|
| 1 | **Batch complete (success)** — all passes done, ≤2 failures | Post completion ping → destroy cron |
| 2 | **Batch complete (failed)** — all passes done, >2 failures | Post failure summary → destroy cron |
| 3 | **Stalled** — no progress for >60 min despite queue running | Attempt queue reset. If still stalled after 2 attempts → fail and destroy |
| 4 | **New batch started** — a new batch run begins while this one is still active | Destroy old cron, create new one for the new batch (only 1 active at a time) |
| 5 | **Manual override** — user deletes the cron manually | Do not auto-recreate. Only create a new cron if user starts a new batch |

**Auto-cleanup:** Cron never auto-recreates after destruction. It is only created again when a new batch is confirmed running through the normal workflow.

---

## Quick Reference

```bash
# 1. Ask the user where to post batch progress updates
#    "Where should I post batch progress updates?"
#    (e.g. Discord channel ID, email, log file, webhook URL)

# 2. Check for existing monitor (substitute your scheduler's command)
openclaw cron list
# or:   crontab -l | grep -i comfy
# or:   systemctl --user list-timers

# 3. If one exists, destroy it
openclaw cron delete {id}
# or:   crontab -e   # then remove the line

# 4. Create new monitor (substitute your scheduler's command)
openclaw cron add \
  --name "ComfyUI Batch Monitor -- {job_name}" \
  --every "30m" \
  --message "Check {batch_name} status: {output_path} -- count outputs and check for errors" \
  --announce --to "{notification_destination}" --channel "{channel_type}" \
  --session "isolated" --timeout-seconds 60

# 5. Send start notification to the destination manually
```
