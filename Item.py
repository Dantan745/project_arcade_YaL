import random

import arcade
from settings import *


class Item(arcade.Sprite):
    """Монета с покадровой анимацией."""

    FRAME_COUNT = 15
    ANIMATION_SPEED = 0.1

    def __init__(
        self,
        pos: tuple,
        all_sprites: arcade.SpriteList,
        items: arcade.SpriteList,
        player,
    ):
        super().__init__()
        self.frames = [
            arcade.load_texture(f'data/items/coin{i}.png')
            for i in range(1, self.FRAME_COUNT + 1)
        ]
        self._frame_index = 0
        self.texture = self.frames[0]
        self.width = self.texture.width * 2
        self.height = self.texture.height * 2
        self.center_x = pos[0]
        self.center_y = pos[1]
        self.player = player
        self._animation_timer = 0.0

        all_sprites.append(self)
        items.append(self)

    def on_update(self, delta_time: float = 1 / 60) -> None:
        self._check_collisions()
        self._animate(delta_time)

    def _check_collisions(self) -> None:
        if arcade.check_for_collision(self, self.player):
            self.remove_from_sprite_lists()
            self.player.take_item()

    def _animate(self, dt: float) -> None:
        self._animation_timer += dt
        if self._animation_timer >= self.ANIMATION_SPEED:
            self._animation_timer -= self.ANIMATION_SPEED
            self._frame_index = (self._frame_index + 1) % self.FRAME_COUNT
            self.texture = self.frames[self._frame_index]
            self.width = self.texture.width * 2
            self.height = self.texture.height * 2
