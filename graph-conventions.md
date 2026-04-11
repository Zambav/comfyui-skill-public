# Graph conventions

## Keep graphs clean

- Prefer stable exported API-format graphs as the base.
- Use meaningful titles when the target workflow will be edited repeatedly.
- Keep save/output nodes obvious.
- Remove dead nodes before publishing a reusable graph.

## Debug checklist

When a graph fails:
1. Reconfirm node classes from `/object_info`.
2. Reconfirm each dropdown value from the target install.
3. Check family-specific encoder/VAE rules.
4. Check custom-node availability.
5. Check history output parsing assumptions.
6. Reduce the graph to the smallest failing case.
