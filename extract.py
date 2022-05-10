import numpy as np
from PIL import Image

import GUI

def is_inner_rgb(rgb: np.ndarray) -> bool:
    #outer_frames = [(255, 255, 255)]
    #inner_frames = [(128, 128, 128), (198, 198, 198)]
    return np.array_equal(rgb, [128, 128, 128]) or np.array_equal(rgb, [198, 198, 198])

def is_edge(arr: np.ndarray, x0: int, y0: int, x1: int, y1: int, threshold: float = 0.8) -> bool:
    outer_limit = int((x1 - x0 + 1) * (y1 - y0 + 1) * (1 - threshold) / 4)
    outer = 0
    for x in range(x0, x1 + 1, 2):
        for y in range(y0, y1 + 1, 2):
            if not is_inner_rgb(arr[y][x]):
                outer += 1
            if outer > outer_limit:
                return False
    return True

def extract_board(original_image_array: np.ndarray, debug_output: str = '') -> tuple[int, int, int, int]:
    debug: bool = debug_output != ''

    image_array = original_image_array.copy()

    height, width = image_array.shape[:2]

    step = 8
    min_x, min_y, max_x, max_y = width, height, -1, -1
    for i in range(int(height / step)):
        for j in range(int(width / step)):
            h, w = i * step, j * step
            if is_inner_rgb(original_image_array[h][w]) \
            and is_inner_rgb(original_image_array[h + step // 2][w]) \
            and is_inner_rgb(original_image_array[h][w + step // 2]) \
            and is_inner_rgb(original_image_array[h + step // 2][w + step // 2]):
                min_x = min(w, min_x)
                max_x = max(w, max_x)
                min_y = min(h, min_y)
                max_y = max(h, max_y)
    min_x = max(min_x - step, 0)
    min_y = max(min_y - step, 0)
    max_x = min(max_x + step * 3 // 2, width - 1)
    max_y = min(max_y + step * 3 // 2, height - 1)

    if debug:
        image_array = GUI.draw_rect(image_array, min_x, min_y, max_x, max_y, np.array([255, 0, 0]))
    
    while not is_edge(original_image_array, min_x, min_y, max_x, min_y):
        min_y += 1
    while not is_edge(original_image_array, min_x, max_y, max_x, max_y):
        max_y -= 1
    while not is_edge(original_image_array, min_x, min_y, min_x, max_y):
        min_x += 1
    while not is_edge(original_image_array, max_x, min_y, max_x, max_y):
        max_x -= 1

    board_width = max_x - min_x + 1
    board_height = max_y - min_y + 1
    
    if debug:
        image_array = GUI.draw_rect(image_array, min_x, min_y, max_x, max_y, np.array([0, 0, 255]))

    # 保存
    if debug:
        Image.fromarray(image_array).save(debug_output)

    return min_x, min_y, max_x - min_x + 1, max_y - min_y + 1, original_image_array[min_y : max_y + 1, min_x : max_x + 1]