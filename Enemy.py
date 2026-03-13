import math

import arcade
from settings import *


class Enemy(arcade.Sprite):
    """Враг, преследующий игрока."""

    def __init__(
        self,
        pos: tuple,
        all_sprites: arcade.SpriteList,
        enemies: arcade.SpriteList,
        player,
    ):
        super().__init__()
        self.texture = arcade.load_texture('data/enemy/enemy.png')
        self.width = self.texture.width * 0.1 - 20
        self.height = self.texture.height * 0.1 - 20
        self.center_x = pos[0]
        self.center_y = pos[1]
        self.player = player
        self._k = 1.0
        self.speed = 150.0

        all_sprites.append(self)
        enemies.append(self)

    def on_update(self, delta_time: float = 1 / 60) -> None:
        dx = self.player.center_x - self.center_x
        dy = self.player.center_y - self.center_y
        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length
        self.center_x += dx * self.speed * delta_time
        self.center_y += dy * self.speed * delta_time

        if arcade.check_for_collision(self, self.player):
            self.remove_from_sprite_lists()
            self.player.take_damage(10)

        self._k += delta_time / 100
        self.speed = 150.0 * self._k
