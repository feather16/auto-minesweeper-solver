import numpy as np

import GUI
from util import Cell

def parse_cell(image_array: np.ndarray) -> Cell:
    h, w = image_array.shape[:2]

    def match(wr: float, hr: float, rgb: tuple[int, int, int], threshold: float = 2.) -> bool:
        return np.linalg.norm(image_array[int(h * hr)][int(w * wr)] - np.array(rgb)) < threshold

    if match(0.075, 0.075, (255, 255, 255)) and match(0.5, 0.5, (0, 128, 0)):
        return Cell.START
    elif match(0.53, 0.53, (0, 0, 255)):
        return Cell.TYPE_1
    elif match(0.32, 0.77, (0, 128, 0)):
        return Cell.TYPE_2
    elif match(0.6, 0.52, (255, 0, 0)):
        return Cell.TYPE_3
    elif match(0.68, 0.51, (0, 0, 128)):
        return Cell.TYPE_4
    elif match(0.53, 0.52, (128, 0, 0)):
        return Cell.TYPE_5
    elif match(0.34, 0.5, (0, 128, 128)):
        return Cell.TYPE_6
    elif match(0.31, 0.28, (0, 0, 0)) and match(0.74, 0.29, (0, 0, 0)) and match(0.58, 0.74, (0, 0, 0)):
        return Cell.TYPE_7
    elif match(0.31, 0.37, (128, 128, 128)):
        return Cell.TYPE_8
    elif match(0.68, 0.41, (0, 0, 0)):
        return Cell.BOMB
    elif match(0.54, 0.73, (0, 0, 0)):
        return Cell.FLAG
    elif match(0.075, 0.075, (255, 255, 255)):
        return Cell.CLOSED
    else:
        return Cell.TYPE_0

def parse_all_cells(info: GUI.Info) -> np.ndarray:
    parsed = np.ndarray((info.cells[::-1]), dtype=np.uint8)
    for j in range(info.cells[1]):
        for i in range(info.cells[0]):
            image_array = info.cut_object(info.cell[j, i])
            parsed[j][i] = int(parse_cell(image_array))
    return parsed