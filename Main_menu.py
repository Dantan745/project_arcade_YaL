import sqlite3
from typing import Callable

import arcade
import arcade.gui
from settings import *


class MainMenu:
    """Главное меню с кнопками, выбором сложности и скина."""

    DIFFICULTIES = ['Легко', 'Средне', 'Тяжело']

    def __init__(
        self,
        manager: arcade.gui.UIManager,
        on_new_game: Callable,
        on_shop: Callable,
        on_exit: Callable,
        on_difficulty_change: Callable,
        on_skin_change: Callable,
    ):
        self.manager = manager
        self._widgets: list[arcade.gui.UIWidget] = []

        self._build_main_buttons(on_new_game, on_shop, on_exit)
        self._build_difficulty_row(on_difficulty_change)
        self._build_skin_row(on_skin_change)
        self._build_score_label()

    # ------------------------------------------------------------------
    # Построение UI
    # ------------------------------------------------------------------

    def _build_main_buttons(self, on_new_game, on_shop, on_exit) -> None:
        v_box = arcade.gui.UIBoxLayout(vertical=True, space_between=20)

        btn_new = arcade.gui.UIFlatButton(text='Новая игра', width=200, height=50)
        btn_shop = arcade.gui.UIFlatButton(text='Магазин', width=200, height=50)
        btn_exit = arcade.gui.UIFlatButton(text='Выход', width=200, height=50)

        @btn_new.event('on_click')
        def _(e):
            on_new_game()

        @btn_shop.event('on_click')
        def _(e):
            on_shop()

        @btn_exit.event('on_click')
        def _(e):
            on_exit()

        v_box.add(btn_new)
        v_box.add(btn_shop)
        v_box.add(btn_exit)

        anchor = self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x='center_x',
                anchor_y='top',
                align_y=-180,
                child=v_box,
            )
        )
        self._widgets.append(anchor)

    def _build_difficulty_row(self, on_difficulty_change: Callable) -> None:
        h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=8)
        for diff in self.DIFFICULTIES:
            btn = arcade.gui.UIFlatButton(text=diff, width=95, height=40)

            @btn.event('on_click')
            def _(e, d=diff):
                on_difficulty_change(d)

            h_box.add(btn)

        anchor = self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x='left',
                anchor_y='bottom',
                align_x=150,
                align_y=100,
                child=h_box,
            )
        )
        self._widgets.append(anchor)

    def _build_skin_row(self, on_skin_change: Callable) -> None:
        available_skins = self._load_available_skins()
        h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=8)
        for s in ['1', '2', '3']:
            label = f'Скин {s}' + ('' if s in available_skins else ' 🔒')
            btn = arcade.gui.UIFlatButton(text=label, width=90, height=40)

            @btn.event('on_click')
            def _(e, sk=s):
                if sk in self._load_available_skins():
                    on_skin_change(int(sk))

            h_box.add(btn)

        anchor = self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x='right',
                anchor_y='bottom',
                align_x=-150,
                align_y=100,
                child=h_box,
            )
        )
        self._widgets.append(anchor)

    def _build_score_label(self) -> None:
        best, money = self._load_best_score()
        label = arcade.gui.UILabel(
            text=f'Рекорд: {best}    Деньги: {money}',
            width=360,
            height=40,
        )
        anchor = self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x='right',
                anchor_y='top',
                align_x=-20,
                align_y=-20,
                child=label,
            )
        )
        self._widgets.append(anchor)

    # ------------------------------------------------------------------
    # Удаление виджетов (при старте игры)
    # ------------------------------------------------------------------

    def remove_all(self) -> None:
        for w in self._widgets:
            w.parent.remove(w)
        self._widgets.clear()

    # ------------------------------------------------------------------
    # Данные
    # ------------------------------------------------------------------

    @staticmethod
    def _load_available_skins() -> list:
        try:
            with open('./data/saved_inf') as f:
                lines = [line.rstrip() for line in f.readlines()]
            return lines[1:]
        except Exception:
            return ['1']

    @staticmethod
    def _load_best_score() -> tuple:
        try:
            con = sqlite3.connect('./data/database/base.sqlite')
            cur = con.cursor()
            cur.execute('SELECT DISTINCT score FROM scores ORDER BY score DESC')
            row = cur.fetchone()
            best = row[0] if row else 0
            with open('./data/saved_inf') as f:
                money = int(f.readlines()[0])
            return best, money
        except Exception:
            return 0, 0
