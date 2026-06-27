# raycastingengine
Software-rendered 3D engine built from scratch in Python, using the same core algorithms as ID Software's _Wolfenstein 3D_ (1992)!

## How does it work?
Raycasting is a rendering technique that simulates a 3D perspective from a 2D top-down map. For every vertical column of pixels on screen, a single ray is fired from the player's position into the world. When the ray strikes a wall, the engine uses the distance to that wall to determine how tall to draw the wall slice. So, closer walls appear taller and walls that are further away are shorter.

## DDA (Digital Differential Analysis)
This replaces the naive approach of stepping along a ray in tiny increments (this is expensive + imprecise) with a method that jumps directly to each grid-line crossing. Because the map is a uniform grid, each step of DDA lands exactly on the NEXT cell boundary in either the X or Y direction, meaning  the algorithm is O(map depth) per ray instead of  O(1/step_size)!

## Texture Mapping
Each wall stores a fractional hit position (0.0–1.0) indicating exactly where within the cell the ray landed. This value selects a single column of the 64×64 texture, which is then scaled vertically to the computed wall height and blitted to the screen. N/S-facing walls receive a 35% brightness reduction relative to E/W walls, providing a cheap directional "shading" effect. Pretty cool!

## Getting Started
Requirements: Python3, PyGame

```bash
pip install pygame
python engine.py
```





