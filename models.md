# Model-family guidance

This file keeps reusable family-level knowledge while avoiding a machine-specific inventory.

## General rule

Confirm actual model filenames from the target install before building the graph.

## Common families

### SDXL-style checkpoint workflows
- Often use `CheckpointLoaderSimple`-style loaders.
- Usually bundle model/CLIP/VAE behavior differently from diffusion-model-only families.
- Good fit for many image workflows and older community graphs.

### FLUX-family workflows
- Frequently require separate diffusion-model, encoder, and VAE decisions.
- Check whether the install expects dual-encoder patterns and a FLUX-specific text encoding path.
- Confirm exact loader node names and text encoder files from `/object_info`.

### WAN-family workflows
- Video-capable workflows often depend on family-specific encoders, VAEs, schedulers, and sometimes multi-stage model loading.
- Confirm whether the chosen variant is text-to-video, image-to-video, animation, or another branch.
- Do not assume one WAN graph fits every WAN model family.

### LTX-family workflows
- Often depend on custom nodes or newer ComfyUI builds.
- Confirm text encoder and scheduler expectations from the target install.
- Validate whether the install uses checkpoint-style loading, dedicated LTX loaders, or both.

## Required checks for any family

For the chosen family, confirm:
- loader node class
- text encoder node class and compatible encoder files
- VAE requirements
- LoRA compatibility expectations
- sampler/scheduler constraints
- custom node requirements
