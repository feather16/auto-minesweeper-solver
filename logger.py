import numpy as np
import time
from image_parse import Cell

timers: dict[str, float] = {}

def print_board(board_array: np.ndarray) -> None:
    height, width = board_array.shape
    for y in range(height):
        for x in range(width):
            print(Cell(board_array[y][x]), end = ' ')
        print('')

class Timer:
    def __init__(self, name: str, detail: int = 3):
        self.name = name
        self.detail = detail
    
    def __enter__(self):
        timers[self.name] = time.time()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.name not in timers:
            print(f"Not found timer '{self.name}'")
        else:
            print(f'{self.name}: {time.time() - timers[self.name]:.{self.detail}f}')