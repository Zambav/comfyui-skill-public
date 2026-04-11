# Compatibility checks

Use this file to prevent cross-family mismatches.

## Validate all four layers

1. Model family
2. Text encoder path
3. VAE path
4. Custom node availability

## Common mismatch patterns

- Trying to reuse an SDXL-style graph for a family that needs separate encoder or diffusion loaders
- Reusing a LoRA trained for one base model on another family
- Assuming a custom node class exists because it existed on another machine
- Reusing example sampler/scheduler settings without confirming support on the current install

## Rule of thumb

If the workflow crosses families or versions, validate from live install data before submit.

## Missing requirement handling

When a needed requirement is absent:
- stop
- name the missing node/model clearly
- say what it is needed for
- offer the nearest compatible alternative if one is known
