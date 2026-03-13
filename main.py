import datetime
import math
import os
import random
import sqlite3

import arcade
import arcade.gui

from Enemy import Enemy
from Item import Item
from Main_menu import MainMenu
from Player import Bullet, Player
from map import MAP_DATA, TileMap
from settings import *
from shop import ShopUI


class Game(arcade.Window):
    """Главный класс игры. Управляет и меню, и игровым процессом."""

    DIFFICULTY_SPAWN = {
        'Легко': 5,
        'Средне': 3,
        'Тяжело': 1,
    }

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, 'Игра')
        arcade.set_background_color(BACKGROUND_COLOR)

        # --- Спрайт-листы ---
        self.all_sprites: arcade.SpriteList = arcade.SpriteList()
        self.enemies: arcade.SpriteList = arcade.SpriteList()
        self.items: arcade.SpriteList = arcade.SpriteList()
        self.bullets: arcade.SpriteList = arcade.SpriteList()

        # --- Состояние ---
        self.play = False
        self.saved = False
        self.skin_num = 1
        self.score = 0
        self.spawn_timer = 0.0
        self.score_timer = 0.0
        self.shoot_timer = 0.0
        self.shoot_interval = 0.5
        self.spawn_interval = self.DIFFICULTY_SPAWN['Средне']
        self.start_time: datetime.datetime | None = None

        # --- Игрок (создаётся при старте) ---
        self.player: Player | None = None

        # --- Звук ---
        self._current_sound_player = None

        # --- Карта ---
        self.tile_map = TileMap(MAP_DATA[random.choice([0, 1, 2])], 100, self.all_sprites)

        # --- Фоновые изображения ---
        bg_files = ['data/maps/canvas.png', 'data/maps/back2.png', 'data/maps/back3.png']
        self.game_background = arcade.load_texture(random.choice(bg_files))
        self.menu_background = arcade.load_texture('data/maps/back.png')

        # --- Скин-текстуры для магазина ---
        self.skin_textures = [
            arcade.load_texture(f'data/player/PlayerLeft{i}.png') for i in range(1, 4)
        ]

        # --- UI ---
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.shop_ui: ShopUI | None = None
        self.shop_visible = False

        self.main_menu = MainMenu(
            self.manager,
            on_new_game=self._start_game,
            on_shop=self._toggle_shop,
            on_exit=arcade.exit,
            on_difficulty_change=self._on_difficulty,
            on_skin_change=self._on_skin,
        )

    # ==================================================================
    # Обработчики Arcade
    # ==================================================================

    def on_draw(self) -> None:
        self.clear()
        if not self.play:
            self._draw_menu()
        else:
            self._draw_game()

    def on_update(self, delta_time: float) -> None:
        if not self.play:
            return

        if not self.player.killed:
            self.spawn_timer += delta_time
            self.score_timer += delta_time
            self.shoot_timer += delta_time

            if self.spawn_timer >= self.spawn_interval:
                self._spawn_enemy()
                self._spawn_item()
                self.spawn_timer = 0.0

            self.all_sprites.on_update(delta_time)
        else:
            if not self.saved:
                self.all_sprites.clear()
                self._save_score()
                self.saved = True

    def on_key_press(self, key: int, modifiers: int) -> None:
        if self.player and not self.player.killed:
            self.player.on_key_press(key)

    def on_key_release(self, key: int, modifiers: int) -> None:
        if self.player and not self.player.killed:
            self.player.on_key_release(key)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if (
            button == arcade.MOUSE_BUTTON_LEFT
            and self.player
            and not self.player.killed
            and self.shoot_timer >= self.shoot_interval
        ):
            dx = x - self.player.center_x
            dy = y - self.player.center_y
            length = math.hypot(dx, dy)
            if length > 0:
                dx /= length
                dy /= length
            bullet = Bullet(
                self.enemies,
                self.player,
                self.all_sprites,
                (self.player.center_x, self.player.center_y),
                (dx, dy),
            )
            self.bullets.append(bullet)
            self.shoot_timer = 0.0

    # ==================================================================
    # Отрисовка
    # ==================================================================

    def _draw_menu(self) -> None:
        arcade.draw_texture_rectangle(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            self.menu_background,
        )
        if self.shop_ui:
            self.shop_ui.draw()
        self.manager.draw()

    def _draw_game(self) -> None:
        if not self.player.killed:
            arcade.draw_texture_rectangle(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                self.game_background,
            )
            self.all_sprites.draw()
            self.player.draw_health_bar()
            self._draw_score()
            self._draw_reload_bar()
        else:
            self._draw_game_over()

    def _draw_score(self) -> None:
        self.score = (
            self.player.counter * 10
            + round(self.score_timer, 1)
            + self.player.kill_counter * 5
        )
        arcade.draw_text(str(int(self.score)), 10, SCREEN_HEIGHT - 50, RED, 36)

    def _draw_reload_bar(self) -> None:
        bar_w = 50
        bar_h = 5
        bx = self.player.center_x
        by = self.player.center_y + self.player.height / 2 + 20

        arcade.draw_rectangle_filled(bx, by, bar_w, bar_h, BLUE)

        fill_w = min(int((self.shoot_timer / self.shoot_interval) * bar_w), bar_w)
        if fill_w > 0:
            arcade.draw_rectangle_filled(
                bx - bar_w / 2 + fill_w / 2, by, fill_w, bar_h, LITE_BLUE
            )

    def _draw_game_over(self) -> None:
        arcade.draw_text(
            'Game Over',
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            RED, 74,
            anchor_x='center', anchor_y='center',
        )
        arcade.draw_text(
            f'Score: {int(self.score)}',
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 90,
            RED, 36, anchor_x='center',
        )
        earned = self.player.coins + self.player.kill_counter * 2
        arcade.draw_text(
            f'Заработано: {earned},  убито: {self.player.kill_counter},  монеток: {self.player.coins}',
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 160,
            RED, 22, anchor_x='center',
        )

    # ==================================================================
    # Логика меню
    # ==================================================================

    def _on_difficulty(self, diff: str) -> None:
        self.spawn_interval = self.DIFFICULTY_SPAWN.get(diff, 3)

    def _on_skin(self, num: int) -> None:
        self.skin_num = num

    def _toggle_shop(self) -> None:
        self.shop_visible = not self.shop_visible
        if self.shop_visible:
            self.shop_ui = ShopUI(self.manager, self.skin_textures)
        else:
            if self.shop_ui:
                self.shop_ui.remove()
                self.shop_ui = None

    def _start_game(self) -> None:
        self.main_menu.remove_all()
        if self.shop_ui:
            self.shop_ui.remove()
            self.shop_ui = None
        self.manager.disable()

        self.player = Player(
            (500, 500),
            self.all_sprites,
            self.tile_map.collide_sprites,
            self.skin_num,
            self._play_sound,
        )
        self.play = True
        self.saved = False
        self.start_time = datetime.datetime.now()
        self._play_sound('soundtrack.mp3', loop=True)

    # ==================================================================
    # Спавн объектов
    # ==================================================================

    def _spawn_enemy(self) -> None:
        side = random.choice(['left', 'right', 'top', 'bottom'])
        if side == 'left':
            x, y = -50, random.randint(0, SCREEN_HEIGHT)
        elif side == 'right':
            x, y = SCREEN_WIDTH + 50, random.randint(0, SCREEN_HEIGHT)
        elif side == 'top':
            x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 50
        else:
            x, y = random.randint(0, SCREEN_WIDTH), -50
        Enemy((x, y), self.all_sprites, self.enemies, self.player)

    def _spawn_item(self) -> None:
        if len(self.items) <= 4:
            coord = (random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50))
            Item(coord, self.all_sprites, self.items, self.player)

    # ==================================================================
    # Сохранение
    # ==================================================================

    def _save_score(self) -> None:
        try:
            con = sqlite3.connect('./data/database/base.sqlite')
            cur = con.cursor()
            duration = str(datetime.datetime.now() - self.start_time)
            cur.execute(
                'INSERT INTO scores(score, time, kill, coins) VALUES(?, ?, ?, ?)',
                (self.score, duration, self.player.kill_counter, self.player.coins),
            )
            con.commit()
        except Exception as e:
            print(f'Ошибка БД: {e}')

        try:
            new_money = self.player.coins + self.player.kill_counter * 2
            with open('./data/saved_inf', 'r') as f:
                lines = f.readlines()
            lines[0] = f'{int(lines[0].strip()) + new_money}\n'
            with open('./data/saved_inf', 'w') as f:
                f.writelines(lines)
        except Exception as e:
            print(f'Ошибка записи: {e}')

    # ==================================================================
    # Звук
    # ==================================================================

    def _play_sound(self, filename: str, loop: bool = False) -> None:
        try:
            sounds_dir = os.path.join(os.path.dirname(__file__), 'Sounds')
            path = os.path.join(sounds_dir, filename)
            sound = arcade.load_sound(path)
            self._current_sound_player = arcade.play_sound(sound, looping=loop)
        except Exception as e:
            print(f'Звук не найден: {e}')

    def _stop_sound(self) -> None:
        if self._current_sound_player:
            arcade.stop_sound(self._current_sound_player)
            self._current_sound_player = None


if __name__ == '__main__':
    game = Game()
    arcade.run()
