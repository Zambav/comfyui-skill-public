# Setup and onboarding

Use this file first when the target ComfyUI install is new, remote, unknown, or only partially documented.

## Goal

Separate reusable ComfyUI guidance from user-specific setup facts.

## First-run checklist

Collect or confirm:
1. Base URL and whether the server is local, remote, or cloud-hosted.
2. ComfyUI version or approximate build age.
3. Installed custom node packs.
4. Available model families the user actually wants to use.
5. Whether `/object_info` is reachable.
6. Output location expectations.
7. Hardware constraints that affect model choice, resolution, frame count, or batch size.

## Discovery-first interview

Ask only for what cannot be discovered automatically.

Suggested order:
1. "What ComfyUI URL should I target?"
2. "Can I inspect `/object_info` on that server?"
3. "Which model family are you trying to use: SDXL, FLUX, WAN, LTX, or something else?"
4. "Do you know which custom nodes are installed, or should I discover them from the API/UI?"
5. "Any hardware limits I should optimize for?"

## Portable setup record

Keep install-specific values in a separate user-owned note or config derived from [config-template.md](config-template.md), for example:
- host/base URL
- known custom nodes
- approved model aliases
- preferred output folder naming
- hardware notes
- workflow templates the user trusts

## Minimum safe assumptions

You may safely assume only that:
- ComfyUI graphs are node-based JSON
- endpoint shapes can drift between versions
- dropdown model values must be confirmed on the target install

Do not assume:
- absolute paths
- the user has your preferred model files
- the user has a specific GPU
- the user has a specific custom node pack
- the user wants local execution
