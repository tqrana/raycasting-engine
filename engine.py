import pygame
from pygame.locals import *
import math

# CONSTANTS
SCREEN_W   = 640
SCREEN_H   = 480
HALF_H     = SCREEN_H // 2
MAX_DEPTH  = 16
MOVE_SPEED = 0.05
ROT_SPEED  = 0.03
TEX_SIZE   = 64
MINIMAP_S  = 8

game_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 2, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 2, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]
MAP_W = len(game_map[0])
MAP_H = len(game_map)
MINIMAP_X = SCREEN_W - MAP_W * MINIMAP_S - 10
MINIMAP_Y = 10


def make_brick_texture():
    surf = pygame.Surface((TEX_SIZE, TEX_SIZE))
    bh, bw = 8, 16   
    for y in range(TEX_SIZE):
        for x in range(TEX_SIZE):
            row    = y // bh
            offset = (row % 2) * (bw // 2)
            mortar = (y % bh == 0) or ((x + offset) % bw == 0)
            if mortar:
                surf.set_at((x, y), (90, 90, 90))
            else:
                n = ((x * 3 + y * 7) * 13) % 25
                surf.set_at((x, y), (150 + n, 60 + n // 2, 40))
    return surf


def make_stone_texture():
    surf = pygame.Surface((TEX_SIZE, TEX_SIZE))
    sz = 16
    for y in range(TEX_SIZE):
        for x in range(TEX_SIZE):
            offset = (y // sz % 2) * (sz // 2)
            seam   = (y % sz == 0) or ((x + offset) % sz == 0)
            if seam:
                surf.set_at((x, y), (70, 70, 70))
            else:
                n = ((x * 5 + y * 11) * 7) % 35
                surf.set_at((x, y), (120 + n, 120 + n, 120 + n))
    return surf


def cast_ray(px, py, dx, dy):
    """
    DDA: steps along grid lines instead of small
    increments, hitting each cell boundary exactly once. Returns
    perp distance to first wall hit, wall type, and fractional hit
    position within the cell.
    """
    mx, my = int(px), int(py)
    ddx = abs(1 / dx) if dx != 0 else float('inf')
    ddy = abs(1 / dy) if dy != 0 else float('inf')
    if dx < 0:
        sx, side_x = -1, (px - mx) * ddx
    else:
        sx, side_x = 1, (mx + 1.0 - px) * ddx

    if dy < 0:
        sy, side_y = -1, (py - my) * ddy
    else:
        sy, side_y = 1, (my + 1.0 - py) * ddy

    side = 0
    cell = 0
    while True:
        if side_x < side_y:
            side_x += ddx
            mx  += sx
            side = 0
        else:
            side_y += ddy
            my  += sy
            side = 1

        if not (0 <= mx < MAP_W and 0 <= my < MAP_H):
            return MAX_DEPTH, 0, 0, 0.0
        cell = game_map[my][mx]
        if cell:
            break
    if side == 0:
        dist   = side_x - ddx
        wall_x = py + dist * dy
    else:
        dist   = side_y - ddy
        wall_x = px + dist * dx

    return dist, side, cell, wall_x - math.floor(wall_x)


def draw_minimap(screen, px, py, dx, dy):
    for row in range(MAP_H):
        for col in range(MAP_W):
            color = (40, 40, 40) if game_map[row][col] == 0 else (180, 180, 180)
            pygame.draw.rect(screen, color,
                             (MINIMAP_X + col * MINIMAP_S,
                              MINIMAP_Y + row * MINIMAP_S,
                              MINIMAP_S - 1, MINIMAP_S - 1))
    pdx = MINIMAP_X + int(px * MINIMAP_S)
    pdy = MINIMAP_Y + int(py * MINIMAP_S)
    pygame.draw.circle(screen, (255, 60, 60), (pdx, pdy), 3)
    pygame.draw.line(screen, (255, 60, 60),
                     (pdx, pdy), (pdx + int(dx * 10), pdy + int(dy * 10)), 2)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption('Raycasting Engine')
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont(None, 28)

    textures = {1: make_brick_texture(), 2: make_stone_texture()}
    px, py         = 1.5,  1.5
    dir_x, dir_y   = 1.0,  0.0
    plane_x, plane_y = 0.0, 0.66

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                return

        keys = pygame.key.get_pressed()

        def rotate(angle):
            nonlocal dir_x, dir_y, plane_x, plane_y
            c, s = math.cos(angle), math.sin(angle)
            dir_x,   dir_y   = dir_x * c - dir_y * s,   dir_x * s + dir_y * c
            plane_x, plane_y = plane_x * c - plane_y * s, plane_x * s + plane_y * c

        def try_move(ddx, ddy):
            nonlocal px, py
            nx, ny = px + ddx, py + ddy
            if 0 <= int(nx) < MAP_W and game_map[int(py)][int(nx)] == 0:
                px = nx
            if 0 <= int(ny) < MAP_H and game_map[int(ny)][int(px)] == 0:
                py = ny

        if keys[K_LEFT]  or keys[K_a]: rotate(-ROT_SPEED)
        if keys[K_RIGHT] or keys[K_d]: rotate( ROT_SPEED)
        if keys[K_UP]    or keys[K_w]: try_move( dir_x * MOVE_SPEED,  dir_y * MOVE_SPEED)
        if keys[K_DOWN]  or keys[K_s]: try_move(-dir_x * MOVE_SPEED, -dir_y * MOVE_SPEED)

        screen.fill((45, 45, 70), (0,      0,      SCREEN_W, HALF_H))
        screen.fill((70, 55, 35), (0,      HALF_H, SCREEN_W, HALF_H))

        for x in range(SCREEN_W):
            cam_x  = 2 * x / SCREEN_W - 1
            ray_dx = dir_x + plane_x * cam_x
            ray_dy = dir_y + plane_y * cam_x

            dist, side, cell, wall_x = cast_ray(px, py, ray_dx, ray_dy)
            if dist <= 0 or dist >= MAX_DEPTH:
                continue

            wall_h   = min(SCREEN_H, int(SCREEN_H / dist))
            wall_top = HALF_H - wall_h // 2

            tex = textures.get(cell)
            if tex:
                tex_x = max(0, min(TEX_SIZE - 1, int(wall_x * TEX_SIZE)))
                col   = pygame.transform.scale(
                            tex.subsurface((tex_x, 0, 1, TEX_SIZE)),
                            (1, wall_h))

                brightness = max(30, int(220 * (1 - dist / MAX_DEPTH)))
                if side == 1:
                    brightness = int(brightness * 0.65)
                col.fill((brightness, brightness, brightness),
                         special_flags=pygame.BLEND_RGB_MULT)

                screen.blit(col, (x, wall_top))

        draw_minimap(screen, px, py, dir_x, dir_y)

        screen.blit(font.render(f'FPS: {int(clock.get_fps())}', True, (255, 0, 100)),
                    (8, 8))

        pygame.display.update()

if __name__ == '__main__':
    main()
