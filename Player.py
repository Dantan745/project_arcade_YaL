import math
from typing import Callable, Optional

import arcade
from settings import *


class Player(arcade.Sprite):
    """Игровой персонаж, управляемый с клавиатуры."""

    def __init__(
        self,
        pos: tuple,
        all_sprites: arcade.SpriteList,
        wall_sprites: arcade.SpriteList,
        skin_num: int,
        play_sound_cb: Optional[Callable] = None,
    ):
        super().__init__()
        self.texture_left = arcade.load_texture(f'data/player/PlayerLeft{skin_num}.png')
        self.texture_right = arcade.load_texture(f'data/player/PlayerRight{skin_num}.png')
        self.texture = self.texture_left
        self.width = 30
        self.height = 30
        self.center_x = pos[0]
        self.center_y = pos[1]

        self.speed = 500
        self.max_health = 100
        self.health = 100
        self.wall_sprites = wall_sprites
        self.killed = False
        self.counter = 0
        self.kill_counter = 0
        self.coins = 0
        self.play_sound_cb = play_sound_cb

        self._move_left = False
        self._move_right = False
        self._move_up = False
        self._move_down = False

        all_sprites.append(self)

    # ------------------------------------------------------------------
    # Ввод
    # ------------------------------------------------------------------

    def on_key_press(self, key: int) -> None:
        if key == arcade.key.A:
            self._move_left = True
        elif key == arcade.key.D:
            self._move_right = True
        elif key == arcade.key.W:
            self._move_up = True
        elif key == arcade.key.S:
            self._move_down = True

    def on_key_release(self, key: int) -> None:
        if key == arcade.key.A:
            self._move_left = False
        elif key == arcade.key.D:
            self._move_right = False
        elif key == arcade.key.W:
            self._move_up = False
        elif key == arcade.key.S:
            self._move_down = False

    # ------------------------------------------------------------------
    # Движение с разрешением коллизий по осям
    # ------------------------------------------------------------------

    def _move_axis(self, dx: float, dy: float) -> None:
        self.center_x += dx
        if arcade.check_for_collision_with_list(self, self.wall_sprites):
            self.center_x -= dx

        self.center_y += dy
        if arcade.check_for_collision_with_list(self, self.wall_sprites):
            self.center_y -= dy

        # Ограничение границами экрана
        self.center_x = max(self.width / 2, min(SCREEN_WIDTH - self.width / 2, self.center_x))
        self.center_y = max(self.height / 2, min(SCREEN_HEIGHT - self.height / 2, self.center_y))

    def on_update(self, delta_time: float = 1 / 60) -> None:
        raw_dx = (int(self._move_right) - int(self._move_left))
        raw_dy = (int(self._move_up) - int(self._move_down))
        length = math.hypot(raw_dx, raw_dy)
        if length > 0:
            raw_dx /= length
            raw_dy /= length

        dx = raw_dx * self.speed * delta_time
        dy = raw_dy * self.speed * delta_time
        self._move_axis(dx, dy)

        if raw_dx > 0:
            self.texture = self.texture_right
        elif raw_dx < 0:
            self.texture = self.texture_left

    # ------------------------------------------------------------------
    # Здоровье
    # ------------------------------------------------------------------

    def take_damage(self, amount: int) -> None:
        self.health -= amount
        if self.play_sound_cb:
            self.play_sound_cb('hp.mp3')
        if self.health <= 0:
            self.killed = True
            if self.play_sound_cb:
                self.play_sound_cb('Game Over.mp3')

    def draw_health_bar(self) -> None:
        bar_width = 50
        bar_height = 5
        bx = self.center_x
        by = self.center_y + self.height / 2 + 10

        arcade.draw_rectangle_filled(bx, by, bar_width, bar_height, BLUE)

        fill_color = GREEN if self.health > 30 else RED
        fill_width = int((self.health / self.max_health) * bar_width)
        if fill_width > 0:
            arcade.draw_rectangle_filled(
                bx - bar_width / 2 + fill_width / 2,
                by,
                fill_width,
                bar_height,
                fill_color,
            )

    def take_item(self) -> None:
        self.counter += 5
        self.coins += 1


class Bullet(arcade.Sprite):
    """Снаряд, летящий в заданном направлении."""

    def __init__(
        self,
        enemies: arcade.SpriteList,
        player: Player,
        all_sprites: arcade.SpriteList,
        pos: tuple,
        direction: tuple,
    ):
        super().__init__()
        self.texture = arcade.load_texture('data/weapons/bomb.png')
        self.width = self.texture.width * 0.1
        self.height = self.texture.height * 0.1
        self.center_x = pos[0]
        self.center_y = pos[1]
        self.direction = direction
        self.enemies = enemies
        self.player = player
        self.speed = 200
        all_sprites.append(self)

    def on_update(self, delta_time: float = 1 / 60) -> None:
        self.center_x += self.direction[0] * self.speed * delta_time
        self.center_y += self.direction[1] * self.speed * delta_time

        if not (0 <= self.center_x <= SCREEN_WIDTH) or not (0 <= self.center_y <= SCREEN_HEIGHT):
            self.remove_from_sprite_lists()
            return

        hit = arcade.check_for_collision_with_list(self, self.enemies)
        if hit:
            for enemy in hit:
                enemy.remove_from_sprite_lists()
                self.player.kill_counter += 1
            self.remove_from_sprite_lists()
