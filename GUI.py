import numpy as np
import pyautogui

from util import Dir8

def draw_rect(arr: np.ndarray, begin_x: int, begin_y: int, end_x: int, end_y: int, rgb: np.ndarray) -> np.ndarray:
    ret = arr.copy()
    for x in range(begin_x, end_x + 1):
        for y in range(begin_y, end_y + 1):
            if x == begin_x or x == end_x or y == begin_y or y == end_y:
                ret[y][x] = rgb
    return ret

class Object:
    def __init__(self, x: float = -1, y: float = -1, w: float = -1, h: float = -1):
        self.x: int = int(x)
        self.y: int = int(y)
        self.w: int = int(w)
        self.h: int = int(h)
    
    def draw_rect(self, image_array: np.ndarray, rgb: np.ndarray) -> np.ndarray:
        return draw_rect(image_array, self.x, self.y, self.x + self.w - 1, self.y + self.h - 1, rgb)
        #for x in range(self.x, self.x + self.w):
        #    for y in range(self.y, self.y + self.h):
        #        if x == self.x or x == self.x + self.w - 1 or y == self.y or y == self.y + self.h - 1:
        #            image_array[y][x] = rgb

    @property
    def pos(self) -> tuple[int, int]:
        return self.x, self.y
    
    @property
    def size(self) -> tuple[int, int]:
        return self.w, self.h

    def __str__(self) -> str:
        return f'({self.x}, {self.y}, {self.w}, {self.h})'
    
    def __repr__(self) -> str:
        return f'GUIObject({self.x}, {self.y}, {self.w}, {self.h})'
        

class Info:
    def __init__(self, offset_x: int, offset_y: int, board_width: int, board_height: int, board_image_array: np.ndarray):

        def get_scale_factor(board_image_array: np.ndarray) -> int:
            x = board_image_array.shape[1] // 3
            s = 0
            for y in range(board_image_array.shape[0]):
                if np.array_equal(board_image_array[y][x], np.array([128, 128, 128])):
                    s = y
                elif np.array_equal(board_image_array[y][x], np.array([255, 255, 255])):
                    return y - s
        
        self.board_image_array: np.ndarray = board_image_array
        scale_factor: int = get_scale_factor(board_image_array)
        cell_size: float = scale_factor * 0.494
        self.board = Object(offset_x, offset_y, board_width, board_height)
        self.bomb_count = [Object()] * 3
        self.bomb_count[0] = Object(0.425 * scale_factor, 0.3875 * scale_factor, 0.35 * scale_factor, 0.65 * scale_factor)
        self.bomb_count[1] = Object(0.8375 * scale_factor, 0.3875 * scale_factor, 0.35 * scale_factor, 0.65 * scale_factor)
        self.bomb_count[2] = Object(1.2375 * scale_factor, 0.3875 * scale_factor, 0.35 * scale_factor, 0.65 * scale_factor)

        estimate_w = (self.board.w - 0.6375 * scale_factor) / cell_size
        estimate_h = (self.board.h - 1.9125 * scale_factor) / cell_size

        # リプレイボタンありの場合
        if 0.08 <= estimate_h - int(estimate_h) < 0.5:
            estimate_h -= 1.16

        self.cells: tuple[int, int] = (
            int(estimate_w + 0.5), 
            int(estimate_h + 0.5)
        )

        self.cell = np.ndarray((self.cells[::-1]), dtype=Object)
        for j in range(self.cells[1]):
            for i in range(self.cells[0]):
                self.cell[j][i] = Object(
                    0.276 * scale_factor + cell_size * i, 
                    1.5625 * scale_factor + cell_size * j, 
                    cell_size, 
                    cell_size
                )

    def __str__(self) -> str:
        return str(vars(self))

    def __repr__(self) -> str:
        return str(vars(self))        

    def cut_object(self, object: Object) -> np.ndarray:
        return self.board_image_array[object.y : object.y + object.h + 1, object.x : object.x + object.w + 1]

    def debug_draw(self) -> np.ndarray:
        image_array = self.board_image_array.copy()

        for i in range(3):
            image_array = self.bomb_count[i].draw_rect(image_array, np.array([0, 255, 0]))

        for i in range(self.cells[0]):
            for j in range(self.cells[1]):
                image_array = self.cell[j, i].draw_rect(image_array, np.array([255, 0, 0]))

        return image_array

    def get_click_pos(self, x: int, y: int) -> tuple[int, int]:
        cell_x: int; cell_y: int; cell_w: int; cell_h: int
        cell_x, cell_y = self.cell[y][x].pos
        cell_w, cell_h = self.cell[y][x].size
        return self.board.x + cell_x + cell_w // 2, self.board.y + cell_y + cell_h // 2

    def open_cell(self, x: int, y: int) -> None:
        cx, cy = self.get_click_pos(x, y)
        pyautogui.click(cx, cy)
    
    def check_cell(self, x: int, y: int) -> None:
        cx, cy = self.get_click_pos(x, y)
        pyautogui.click(cx, cy, button=pyautogui.RIGHT)

    def update(self) -> None:
        image_pil = pyautogui.screenshot()
        image_array = np.array(image_pil)
        self.board_image_array = image_array[
            self.board.y : self.board.y + self.board.h, 
            self.board.x : self.board.x + self.board.w
        ]