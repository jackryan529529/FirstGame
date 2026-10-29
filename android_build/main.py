from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
import os
import random

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(APP_DIR, 'assets')

# Each piece is a list of occupied (row, column) offsets.
SHAPES = [
    [(0, 0)],
    [(0, 0), (0, 1)],
    [(0, 0), (0, 1), (0, 2)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 0), (0, 1), (1, 0), (1, 1)],
    [(0, 0), (1, 0), (1, 1)],
    [(0, 1), (1, 0), (1, 1)],
    [(0, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (2, 0), (2, 1)],
    [(0, 0), (0, 1), (0, 2), (1, 1)],
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    [(0, 0), (0, 1), (0, 2), (0, 3)],
]
BG = get_color_from_hex('#10182D')
PANEL = get_color_from_hex('#202D4D')
BLUE = get_color_from_hex('#328BFF')
PINK = get_color_from_hex('#FF729F')
GOLD = get_color_from_hex('#FFBE55')
WHITE = get_color_from_hex('#F5F7FF')
MUTED = get_color_from_hex('#B9C5E5')

class SoundManager:
    def __init__(self):
        self.music_volume = 0.45
        self.fx_volume = 0.75
        self.muted = False
        self.current_music = None
        self.effects = {}
        for name in ('pop', 'clear', 'combo', 'nomoves'):
            path = os.path.join(ASSET_DIR, name + '.wav')
            sound = SoundLoader.load(path) if os.path.exists(path) else None
            self.effects[name] = sound

    def play_music(self, filename):
        path = os.path.join(ASSET_DIR, filename)
        if self.current_music:
            try:
                self.current_music.stop()
            except Exception:
                pass
        self.current_music = SoundLoader.load(path) if os.path.exists(path) else None
        if self.current_music:
            self.current_music.loop = True
            self.current_music.volume = 0 if self.muted else self.music_volume
            self.current_music.play()

    def effect(self, name):
        sound = self.effects.get(name)
        if sound:
            try:
                sound.stop()
                sound.volume = 0 if self.muted else self.fx_volume
                sound.play()
            except Exception:
                pass

    def update_volume(self):
        if self.current_music:
            self.current_music.volume = 0 if self.muted else self.music_volume

class MenuButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.color = WHITE
        self.bold = True
        self.font_size = '20sp'
        self.size_hint_y = None
        self.height = dp(54)

class TitleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(18))
        root.add_widget(Widget(size_hint_y=0.4))
        title = Label(text='BLOCK\nPUZZLE', font_size='42sp', bold=True, color=WHITE,
                      halign='center', valign='middle', size_hint_y=None, height=dp(150))
        title.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        root.add_widget(title)
        subtitle = Label(text='Fit the blocks. Clear the lines. Have fun!', font_size='16sp', color=MUTED,
                         size_hint_y=None, height=dp(45), halign='center')
        root.add_widget(subtitle)
        play = MenuButton(text='▶  PLAY', background_color=GOLD, color=get_color_from_hex('#17213A'))
        play.bind(on_release=lambda *_: self.begin_welcome())
        root.add_widget(play)
        root.add_widget(Widget(size_hint_y=0.6))
        root.add_widget(Label(text='A little puzzle, made with love', color=MUTED, font_size='13sp', size_hint_y=None, height=dp(30)))
        self.add_widget(root)

    def begin_welcome(self):
        self.manager.current = 'welcome'
        self.manager.app.sounds.play_music('love_music.wav')

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(12))
        root.add_widget(Widget(size_hint_y=0.05))
        photo_path = os.path.join(ASSET_DIR, 'wife_photo.jpg')
        if os.path.exists(photo_path):
            photo = Image(source=photo_path, fit_mode='contain', size_hint_y=0.66)
            root.add_widget(photo)
        else:
            root.add_widget(Label(text='❤️', font_size='72sp', size_hint_y=0.66))
        msg = Label(text='Welcome, My Love ❤️', font_size='27sp', bold=True, color=PINK,
                    size_hint_y=None, height=dp(60), halign='center')
        root.add_widget(msg)
        go = MenuButton(text="Let's Play!", background_color=PINK)
        go.bind(on_release=self.start_game)
        root.add_widget(go)
        root.add_widget(Widget(size_hint_y=0.08))
        self.add_widget(root)

    def start_game(self, *_):
        self.manager.app.sounds.play_music('game_music.wav')
        self.manager.get_screen('game').game.new_game()
        self.manager.current = 'game'

class GameBoard(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(8), **kwargs)
        self.app = app
        self.matrix = [[0 for _ in range(8)] for _ in range(8)]
        self.score = 0
        self.best = 0
        self.pieces = []
        self.selected = None
        self.game_over = False
        self.cell_buttons = {}

        header = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.score_label = Label(text='SCORE  0', color=WHITE, bold=True, font_size='20sp')
        header.add_widget(self.score_label)
        restart = MenuButton(text='Restart', background_color=BLUE)
        restart.font_size = '14sp'; restart.height = dp(42); restart.size_hint_x = 0.34
        restart.bind(on_release=lambda *_: self.new_game())
        header.add_widget(restart)
        self.add_widget(header)

        self.status = Label(text='Choose a piece, then tap where it should start.', color=MUTED,
                            size_hint_y=None, height=dp(34), font_size='13sp')
        self.add_widget(self.status)

        board_wrap = BoxLayout(orientation='vertical', padding=dp(2), size_hint_y=0.62)
        self.board = GridLayout(cols=8, rows=8, spacing=dp(3), padding=dp(3))
        for r in range(8):
            for c in range(8):
                b = Button(text='', background_normal='', background_color=[0.13, 0.18, 0.29, 1])
                b.bind(on_release=lambda inst, rr=r, cc=c: self.place_selected(rr, cc))
                self.board.add_widget(b)
                self.cell_buttons[(r, c)] = b
        board_wrap.add_widget(self.board)
        self.add_widget(board_wrap)

        self.tray = GridLayout(cols=3, rows=1, spacing=dp(6), size_hint_y=None, height=dp(104))
        self.add_widget(self.tray)
        self.add_widget(Label(text='Sound', color=MUTED, size_hint_y=None, height=dp(22), font_size='13sp'))
        controls = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        self.music_slider = Slider(min=0, max=1, value=self.app.sounds.music_volume)
        self.music_slider.bind(value=self.set_music_volume)
        controls.add_widget(Label(text='Music', color=WHITE, size_hint_x=0.22, font_size='12sp'))
        controls.add_widget(self.music_slider)
        self.fx_slider = Slider(min=0, max=1, value=self.app.sounds.fx_volume)
        self.fx_slider.bind(value=self.set_fx_volume)
        controls.add_widget(Label(text='FX', color=WHITE, size_hint_x=0.12, font_size='12sp'))
        controls.add_widget(self.fx_slider)
        self.add_widget(controls)
        mute = MenuButton(text='Mute / Unmute', background_color=PANEL)
        mute.height = dp(38); mute.font_size = '14sp'
        mute.bind(on_release=lambda *_: self.toggle_mute())
        self.add_widget(mute)
        self.new_game()

    def set_music_volume(self, _, value):
        self.app.sounds.music_volume = value
        self.app.sounds.update_volume()

    def set_fx_volume(self, _, value):
        self.app.sounds.fx_volume = value

    def toggle_mute(self):
        self.app.sounds.muted = not self.app.sounds.muted
        self.app.sounds.update_volume()

    def new_game(self):
        self.matrix = [[0 for _ in range(8)] for _ in range(8)]
        self.score = 0
        self.pieces = [random.choice(SHAPES) for _ in range(3)]
        self.selected = None
        self.game_over = False
        self.status.text = 'Choose a piece, then tap where it should start.'
        self.refresh_board()
        self.refresh_tray()
        self.update_score()

    def update_score(self):
        self.score_label.text = f'SCORE  {self.score}'

    def refresh_board(self):
        for r in range(8):
            for c in range(8):
                btn = self.cell_buttons[(r, c)]
                btn.background_color = PINK if self.matrix[r][c] else [0.13, 0.18, 0.29, 1]

    def shape_text(self, shape):
        h = max(r for r, c in shape) + 1
        w = max(c for r, c in shape) + 1
        return '\n'.join(''.join('■' if (r, c) in shape else ' ' for c in range(w)) for r in range(h))

    def refresh_tray(self):
        self.tray.clear_widgets()
        for i, shape in enumerate(self.pieces):
            if shape is None:
                b = Button(text='Used', disabled=True, background_normal='', background_color=PANEL, color=MUTED)
            else:
                b = Button(text=self.shape_text(shape), font_size='18sp', background_normal='',
                           background_color=GOLD if self.selected == i else BLUE, color=WHITE)
                b.bind(on_release=lambda _, idx=i: self.select_piece(idx))
            self.tray.add_widget(b)

    def select_piece(self, index):
        if self.game_over or self.pieces[index] is None:
            return
        self.selected = index
        self.status.text = 'Now tap a starting cell on the board.'
        self.refresh_tray()

    def can_place(self, shape, row, col):
        for dr, dc in shape:
            rr, cc = row + dr, col + dc
            if rr < 0 or rr >= 8 or cc < 0 or cc >= 8 or self.matrix[rr][cc]:
                return False
        return True

    def place_selected(self, row, col):
        if self.game_over or self.selected is None:
            return
        shape = self.pieces[self.selected]
        if shape is None:
            return
        if not self.can_place(shape, row, col):
            self.status.text = 'That piece does not fit there. Try another spot.'
            return
        for dr, dc in shape:
            self.matrix[row + dr][col + dc] = 1
        self.pieces[self.selected] = None
        self.selected = None
        self.score += len(shape)
        self.app.sounds.effect('pop')
        rows = [r for r in range(8) if all(self.matrix[r][c] for c in range(8))]
        cols = [c for c in range(8) if all(self.matrix[r][c] for r in range(8))]
        clear_count = len(rows) + len(cols)
        if clear_count:
            for r in rows:
                for c in range(8): self.matrix[r][c] = 0
            for c in cols:
                for r in range(8): self.matrix[r][c] = 0
            self.score += clear_count * 100
            self.app.sounds.effect('combo' if clear_count >= 2 else 'clear')
            self.status.text = f'Great! {clear_count} line(s) cleared!'
        else:
            self.status.text = 'Nice placement!'
        if all(piece is None for piece in self.pieces):
            self.pieces = [random.choice(SHAPES) for _ in range(3)]
        self.refresh_board()
        self.refresh_tray()
        self.update_score()
        if not any(self.can_place(piece, r, c) for piece in self.pieces if piece for r in range(8) for c in range(8)):
            self.game_over = True
            self.status.text = f'No moves left! Final score: {self.score}. Tap Restart to play again.'
            self.app.sounds.effect('nomoves')
        elif clear_count >= 2:
            self.status.text = f'Combo! {clear_count} lines cleared!'

class GameScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.game = GameBoard(app)
        self.add_widget(self.game)

class BlockBlastApp(App):
    def build(self):
        self.title = 'Block Puzzle - Made with Love'
        Window.clearcolor = BG
        self.sounds = SoundManager()
        manager = ScreenManager(transition=FadeTransition(duration=0.25))
        manager.app = self
        manager.add_widget(TitleScreen(name='title'))
        manager.add_widget(WelcomeScreen(name='welcome'))
        manager.add_widget(GameScreen(self, name='game'))
        self.sounds.play_music('title_music.wav')
        return manager

if __name__ == '__main__':
    BlockBlastApp().run()
