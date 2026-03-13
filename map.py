import arcade
from settings import *

MAP_DATA = [
    [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 2, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
     [0, 0, 0, 0, 0, 1, 0, 0, 0, 0]],
    [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 1, 0, 0, 0, 0, 0, 2, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
     [0, 0, 0, 0, 0, 1, 0, 0, 0, 0]],
    [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 2, 0, 2, 0, 2, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 2, 0],
     [0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 2, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 2, 0, 2, 0, 2, 0, 2, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
]


class CollisionSprite(arcade.Sprite):
    """Тайл-препятствие на карте."""

    def __init__(self, center_x: float, center_y: float, file: str):
        super().__init__()
        self.texture = arcade.load_texture(f'data/maps/{file}')
        self.width = 100
        self.height = 100
        self.center_x = center_x
        self.center_y = center_y


class TileMap:
    """Генерирует карту из двумерного массива и заполняет списки спрайтов."""

    TILE_FILES = {
        1: 'block.png',
        2: 'stone2.png',
    }
    COLLIDABLE = {1, 2}

    def __init__(self, map_data: list, tile_size: int, all_sprites: arcade.SpriteList):
        self.map_data = map_data
        self.tile_size = tile_size
        self.collide_sprites = arcade.SpriteList()

        for row_index, row in enumerate(map_data):
            for col_index, tile_type in enumerate(row):
                if tile_type in self.COLLIDABLE:
                    cx = col_index * tile_size + tile_size // 2
                    # Arcade: y=0 внизу, поэтому переворачиваем ось Y
                    cy = SCREEN_HEIGHT - (row_index * tile_size + tile_size // 2)
                    sprite = CollisionSprite(cx, cy, self.TILE_FILES[tile_type])
                    all_sprites.append(sprite)
                    self.collide_sprites.append(sprite)
