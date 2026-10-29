from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
import random

SHAPES = [
    [[1, 1]],
    [[1, 1, 1]],
    [[1]],
    [[1, 1], [1, 1]],
    [[1, 0], [1, 1]]
]

class GameCell(Button):
    def __init__(self, row, col, **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        self.background_normal = ''
        self.background_color = [0.15, 0.15, 0.18, 1]

class BlockBlastClone(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)
        self.score = 0
        self.selected_shape = None
        self.grid_matrix = [[0]*8 for _ in range(8)]
        
        self.score_label = Label(text='SCORE: 0', font_size=28, size_hint_y=0.1)
        self.add_widget(self.score_label)
        
        self.grid_layout = GridLayout(cols=8, spacing=2, size_hint_y=0.6)
        self.cells = {}
        for r in range(8):
            for c in range(8):
                cell = GameCell(r, c)
                cell.bind(on_release=self.grid_cell_click)
                self.grid_layout.add_widget(cell)
                self.cells[(r, c)] = cell
        self.add_widget(self.grid_layout)
        
        self.tray_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.3)
        self.add_widget(self.tray_layout)
        self.refresh_tray()

    def refresh_tray(self):
        self.tray_layout.clear_widgets()
        for i in range(3):
            shape = random.choice(SHAPES)
            btn = Button(text=f'Shape {i+1}\n({len(shape)}x{len(shape[0])})', background_color=[0.2, 0.6, 0.8, 1])
            btn.bind(on_release=lambda x, s=shape: self.select_shape(s))
            self.tray_layout.add_widget(btn)

    def select_shape(self, shape):
        self.selected_shape = shape

    def grid_cell_click(self, instance):
        if not self.selected_shape:
            return
        start_r, start_c = instance.row, instance.col
        shape_h = len(self.selected_shape)
        shape_w = len(self.selected_shape[0])
        
        if start_r + shape_h > 8 or start_c + shape_w > 8:
            return
            
        for r in range(shape_h):
            for c in range(shape_w):
                if self.selected_shape[r][c] == 1 and self.grid_matrix[start_r + r][start_c + c] == 1:
                    return
                    
        for r in range(shape_h):
            for c in range(shape_w):
                if self.selected_shape[r][c] == 1:
                    rr, cc = start_r + r, start_c + c
                    self.grid_matrix[rr][cc] = 1
                    self.cells[(rr, cc)].background_color = [0.9, 0.3, 0.4, 1]
                    
        self.selected_shape = None
        self.check_line_clears()

    def check_line_clears(self):
        rows_to_clear = [r for r in range(8) if all(self.grid_matrix[r][c] == 1 for c in range(8))]
        cols_to_clear = [c for c in range(8) if all(self.grid_matrix[r][c] == 1 for r in range(8)) ]
        
        for r in rows_to_clear:
            for c in range(8):
                self.grid_matrix[r][c] = 0
                self.cells[(r, c)].background_color = [0.15, 0.15, 0.18, 1]
        for c in cols_to_clear:
            for r in range(8):
                self.grid_matrix[r][c] = 0
                self.cells[(r, c)].background_color = [0.15, 0.15, 0.18, 1]
                
        clears = len(rows_to_clear) + len(cols_to_clear)
        if clears > 0:
            self.score += (clears * 100)
            self.score_label.text = f'SCORE: {self.score}'
            
        if random.random() < 0.2:
            self.refresh_tray()

class BlockBlastApp(App):
    def build(self):
        return BlockBlastClone()

if __name__ == '__main__':
    BlockBlastApp().run()
