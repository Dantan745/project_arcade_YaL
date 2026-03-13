# Roguelike Arcade

Двумерная рогалик-игра с видом сверху, переписанная с фреймворка **PyGame** на **Python Arcade**.

## Описание

Игрок оказывается на процедурно выбранной карте с препятствиями и должен выживать как можно дольше, отстреливая врагов и подбирая монеты. Очки начисляются за выживаемость, убийства и подобранные предметы. Между раундами можно потратить заработанные монеты в магазине на новые скины персонажа.

### Механики

- **Движение** — WASD, с разрешением коллизий по осям.
- **Стрельба** — клик левой кнопкой мыши: снаряд летит в направлении курсора.
- **Перезарядка** — над персонажем отображается полоска перезарядки (интервал 0.5 с).
- **Враги** — появляются с краёв экрана, преследуют игрока; скорость постепенно растёт.
- **Монеты** — анимированные подбираемые предметы; при контакте с игроком засчитываются.
- **Здоровье** — у игрока 100 HP; каждый касание врага снимает 10. Полоска над персонажем меняет цвет на красный при критическом состоянии.
- **Магазин** — три скина, каждый можно купить один раз. Прогресс сохраняется в `data/saved_inf`.
- **База данных** — результаты каждой партии (счёт, длительность, убийства, монеты) записываются в SQLite (`data/database/base.sqlite`). Лучший результат отображается в меню.
- **Сложность** — три режима (Легко / Средне / Тяжело), влияющие на частоту появления врагов.

## Структура проекта

```
rogulike-arcade/
├── main.py          # Точка входа, класс Game (arcade.Window)
├── Player.py        # Классы Player и Bullet
├── Enemy.py         # Класс Enemy
├── Item.py          # Класс Item (монета с анимацией)
├── map.py           # Классы TileMap и CollisionSprite; данные карт
├── shop.py          # Класс ShopUI (покупка скинов)
├── Main_menu.py     # Класс MainMenu (UI главного меню)
├── settings.py      # Константы (размер экрана, цвета)
├── requirements.txt
├── data/
│   ├── player/      # Текстуры игрока (PlayerLeft1-3, PlayerRight1-3)
│   ├── enemy/       # Текстура врага
│   ├── weapons/     # Текстура снаряда (bomb.png)
│   ├── items/       # Кадры анимации монеты (coin1-15.png)
│   ├── maps/        # Фоны и тайлы карты
│   ├── database/    # base.sqlite
│   └── saved_inf    # Деньги и купленные скины (текстовый файл)
└── Sounds/          # Звуковые файлы (soundtrack.mp3, hp.mp3, Game Over.mp3)
```

## Установка и запуск

```bash
pip install -r requirements.txt
python main.py
```

## Отличия от PyGame-версии

| PyGame | Arcade |
|---|---|
| `pygame.sprite.Sprite` | `arcade.Sprite` |
| `pygame.sprite.Group` | `arcade.SpriteList` |
| `pygame.sprite.spritecollide` | `arcade.check_for_collision_with_list` |
| `pygame.image.load` | `arcade.load_texture` |
| `pygame.mixer.Sound` | `arcade.load_sound` + `arcade.play_sound` |
| `pygame_gui.UIManager` | `arcade.gui.UIManager` |
| `pygame.draw.rect` | `arcade.draw_rectangle_filled` |
| `pygame.font.render` | `arcade.draw_text` |
| Главный цикл вручную | `arcade.Window.on_update / on_draw` |
| `pygame.math.Vector2` | `math.hypot` + простые float |
| Y=0 сверху (вниз ↓) | Y=0 снизу (вверх ↑) |

## Авторы

- **Александра Дорофеева**
- **Иваненко Даниил**