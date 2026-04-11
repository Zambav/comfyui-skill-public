# LoRA guidance

## Core rule

Treat every LoRA as family-specific until proven otherwise.

## Before loading a LoRA

Confirm:
- the LoRA filename exists on the target install
- the target base model family matches the LoRA's training family
- the graph uses the correct loader path for that family
- any text-encoder-side LoRA behavior is supported by the nodes on the install

## Portable instruction pattern

Say:
- "Confirm the available LoRAs from the install"
- "Verify this LoRA was trained for the selected base model family"
- "Apply conservative strengths first, then tune"

Do not say:
- "Use my local favorite LoRA"
- "Assume this named LoRA exists"

## Stacking

When stacking multiple LoRAs:
- add them one at a time
- keep strengths conservative initially
- test for shape/key mismatches after each addition
