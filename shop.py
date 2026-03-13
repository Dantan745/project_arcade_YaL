import arcade
import arcade.gui
from settings import *


class ShopUI:
    """Интерфейс магазина скинов."""

    SKIN_PRICES = [100, 150, 200]

    def __init__(self, manager: arcade.gui.UIManager, skin_textures: list):
        self.manager = manager
        self.skin_textures = skin_textures

        with open('./data/saved_inf', 'r') as f:
            lines = [line.rstrip() for line in f.readlines()]
        self.money = int(lines[0])
        self.skins = lines[1:]

        self._widgets: list[arcade.gui.UIWidget] = []
        self._build_ui()

    def _build_ui(self) -> None:
        h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=50)

        for i, price in enumerate(self.SKIN_PRICES):
            btn = arcade.gui.UIFlatButton(text=f'Купить за {price}', width=150, height=50)

            @btn.event('on_click')
            def on_click(event, idx=i):
                self._buy_skin(idx)

            h_box.add(btn)

        anchor = self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x='center_x',
                anchor_y='center_y',
                align_y=-120,
                child=h_box,
            )
        )
        self._widgets.append(anchor)

    def draw(self) -> None:
        """Рисует превью скинов над кнопками покупки."""
        for i, texture in enumerate(self.skin_textures):
            x = 200 + i * 200
            y = SCREEN_HEIGHT // 2 + 80
            w = texture.width * 3
            h = texture.height * 3
            arcade.draw_texture_rectangle(x, y, w, h, texture)

    def remove(self) -> None:
        for w in self._widgets:
            w.parent.remove(w)
        self._widgets.clear()

    def _buy_skin(self, skin_index: int) -> None:
        label = str(skin_index + 1)
        if label in self.skins:
            print('Такой скин уже есть')
            return
        if self.SKIN_PRICES[skin_index] > self.money:
            print('Недостаточно денег')
            return

        self.money -= self.SKIN_PRICES[skin_index]
        self.skins.append(label)
        self._write_data(skin_index)
        print(f'Скин {label} куплен!')

    def _write_data(self, skin_index: int) -> None:
        with open('./data/saved_inf', 'r') as f:
            lines = f.readlines()
        lines[0] = f'{self.money}\n'
        lines.append(f'{skin_index + 1}\n')
        with open('./data/saved_inf', 'w') as f:
            f.writelines(lines)
