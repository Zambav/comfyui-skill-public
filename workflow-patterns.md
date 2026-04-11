# Workflow patterns

## Core rule

Build workflows from discovered capabilities, not from remembered local graphs.

## Programmatic graph rules

- Node IDs in API JSON should be strings.
- Track node IDs centrally to avoid silent overwrite.
- Keep links explicit: `[source_node_id, output_index]`.
- Use filename-only values for model fields unless a confirmed subdirectory path is required.
- Avoid absolute filesystem paths inside graph JSON.

## Template-first strategy

Preferred order:
1. Start from a known-good workflow exported in API format, if one exists for the target install.
2. Patch only the parameters required for the task.
3. Fall back to constructing a graph from scratch only when no suitable template exists.

## Validation before submit

Check:
- every referenced node class exists in `/object_info`
- every model/LoRA/VAE/encoder value is available on the target install
- family-specific encoder and VAE rules are satisfied
- custom node dependencies are present

## Portability mindset

Write helpers so the caller provides:
- base URL
- checkpoint / UNet / encoder / VAE names
- LoRA names
- output naming rules
- optional custom-node variants

Do not bury those choices as hidden defaults unless they are generic fallbacks.
