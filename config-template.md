# Config template

Use this as a user-owned setup record, not as a hardcoded skill assumption.

```yaml
comfyui:
  base_url: http://127.0.0.1:8188
  websocket_url: ws://127.0.0.1:8188/ws
  install_type: local   # local | remote | cloud
  version_notes: ""
  custom_nodes:
    - name: ""
      purpose: ""
  model_aliases:
    image_default: ""
    video_default: ""
    flux_default: ""
    wan_default: ""
    ltx_default: ""
  output_rules:
    default_subfolder: ""
    filename_prefix: ""
  hardware:
    gpu: ""
    vram_gb: ""
    notes: ""
```

Replace example defaults with the user's real environment before relying on them.
