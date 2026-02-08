# 3D Models for SkillMine

## Wolf Model

To use the 3D wolf model from Sketchfab:

1. **Download the model:**
   - Visit: https://sketchfab.com/3d-models/wolf-posed-4359f6ed9e2a494d86b6b0e514556855
   - Click the "Download 3D Model" button (requires free Sketchfab account)
   - Choose one of these formats:
     - **OBJ** (recommended for Ursina) - includes textures
     - **GLTF** - modern format
     - **FBX** - also works well

2. **Extract and place the model:**
   - Extract the downloaded file
   - Rename the main model file to `wolf.obj` (or `wolf.gltf`, `wolf.fbx`)
   - Place it in this folder: `assets/models/`
   - If there are texture files (.png, .jpg), place them here too

3. **The game will automatically use it:**
   - The pet system will automatically detect and load `wolf.obj` (or other formats)
   - If not found, it falls back to a simple cube shape
   - You may need to adjust the scale in `config.py` under STARTER_PETS

## Adjusting Model Scale

If the model appears too large or small, edit the `model_scale` in `src/ai/pets.py`:

```python
model_scale: tuple = (0.5, 0.5, 0.5)  # Adjust these values
```

Or adjust the pet's scale in `config.py` under `STARTER_PETS['wolf']`.

## Other Pet Models

You can add custom models for other pets (owl, turtle) using the same process:
- Place `owl.obj` or `turtle.obj` in this folder
- The game will automatically use them
