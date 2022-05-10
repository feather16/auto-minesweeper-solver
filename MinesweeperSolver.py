from numpy.core.numeric import base_repr
from numpy.lib import utils
from numpy.lib.function_base import append
import pyautogui
import numpy as np
from PIL import Image
from pprint import pprint

import util
import window
import GUI
import extract
import image_parse
import logger

Cell = util.Cell
Dir8 = util.Dir8

window.try_set_minesweeper_foreground('Minesweeper Online') #後で変える

# スクリーンショットを撮る
image_pil = pyautogui.screenshot()
image_array = np.array(image_pil)

# 盤面を切り抜く
offset_x, offset_y, board_width, board_height, board_image_array = extract.extract_board(image_array)

# セルの位置などを特定
board_gui_info = GUI.Info(offset_x, offset_y, board_width, board_height, board_image_array)
#Image.fromarray(board_gui_info.debug_draw()).save('my_image/cell_test.png')

# count_around? around_indices?

def no_need_to_open(cell_array: np.ndarray, x: int, y: int) -> bool:
    if cell_array[y][x] == Cell.CLOSED:
        return False
    for i in range(8):
        d = Dir8(i)
        if 0 <= x + d.x < cell_array.shape[1] and 0 <= y + d.y < cell_array.shape[0]:
            if cell_array[y + d.y][x + d.x] == Cell.CLOSED:
                return False
    return True

def calculate(cell_array: np.ndarray):
    # 変数の用意
    #cell_expected_array = np.full(cell_array.shape + (8,), 0, np.int16)
    openable_array = np.full(cell_array.shape, False, np.bool8)
    checkable_array = np.full(cell_array.shape, False, np.bool8)
    cell_sets: list[tuple[set[(int, int)], int]] = list()

    # どこも開いていない場合
    if np.all(cell_array == int(Cell.CLOSED)):
        openable_array[0][0] = True
        return openable_array, checkable_array

    for y in range(cell_array.shape[0]):
        for x in range(cell_array.shape[1]):

            if Cell(cell_array[y][x]).is_number() and cell_array[y][x] != Cell.TYPE_0:

                closed_indices: list[int] = []
                flag_indices: list[int] = []

                # closedとflagのカウント
                for i in range(8):
                    d = Dir8(i)
                    if 0 <= x + d.x < cell_array.shape[1] and 0 <= y + d.y < cell_array.shape[0]:
                        d_cell = Cell(cell_array[y + d.y][x + d.x])
                        if d_cell == Cell.CLOSED:
                            closed_indices.append(i)
                        elif d_cell == Cell.FLAG:
                            flag_indices.append(i)

                # 周囲の残り爆弾数
                remaining_bombs: int = cell_array[y][x] - len(flag_indices)

                # そのまま開けられる場合
                if remaining_bombs == 0:
                    openable_array[y][x] = True

                # チェックできる場合
                if remaining_bombs == len(closed_indices):
                    for closed_index in closed_indices:
                        d = Dir8(closed_index)
                        checkable_array[y + d.y][x + d.x] = True

                # cell_sets
                if 0 < remaining_bombs < len(closed_indices):
                    cell_set: set[tuple[int, int]] = set()
                    for closed_index in closed_indices:
                        d = Dir8(closed_index)
                        cell_set.add((x + d.x, y + d.y))
                    cell_sets.append((cell_set, remaining_bombs))

            # startは必ず開ける
            elif Cell(cell_array[y][x]) == Cell.START:
                openable_array[y][x] = True

    def check_cell_sets(
        subset: tuple[set[(int, int)], int], 
        superset: tuple[set[(int, int)], int]
        ) -> None:

        diff_cell_set: set[tuple[int, int]] = superset[0] - subset[0] # len > 0
        diff_bombs: int = superset[1] - subset[1]
        if diff_bombs == 0:
            for x, y in diff_cell_set:
                openable_array[y][x] = True
        elif diff_bombs == len(diff_cell_set):
            for x, y in diff_cell_set:
                checkable_array[y][x] = True
        else:
            # 既にある場合は追加しない
            exists = False
            for cell_set in cell_sets:
                if cell_set[0] == diff_cell_set:
                    exists = True
                    break

            if not exists:
                cell_sets.append((diff_cell_set, diff_bombs))

    # cell_setsの重複を消す
    j = len(cell_sets) - 1
    while j >= 1:
        i = j - 1
        while i >= 0:
            if cell_sets[i] == cell_sets[j]:
                cell_sets.pop(j)
                break
            i -= 1
        j -= 1

    j = 1
    while j < len(cell_sets):
        for i in range(j):
            if len(cell_sets[i][0]) > 0 and len(cell_sets[j][0]):
                if cell_sets[i][0] < cell_sets[j][0]:
                    check_cell_sets(cell_sets[i], cell_sets[j])
                elif cell_sets[j][0] < cell_sets[i][0]:
                    check_cell_sets(cell_sets[j], cell_sets[i])
        j += 1

    return openable_array, checkable_array

def solve(board_gui_info: GUI.Info) -> None:
    loop_count = 0
    while True:

        with logger.Timer(f'Scanned Board {loop_count}'):
            board_gui_info.update()

        with logger.Timer(f'Identified Cells {loop_count}'):
            cell_array = image_parse.parse_all_cells(board_gui_info)

        logger.print_board(cell_array)

        changed = False

        with logger.Timer(f'Calculated {loop_count}'):
            openable_array, checkable_array = calculate(cell_array)

        with logger.Timer(f'Executed {loop_count}'):
            for y in range(cell_array.shape[0]):
                for x in range(cell_array.shape[1]):
                    if checkable_array[y][x]:
                        board_gui_info.check_cell(x, y)
                        cell_array[y][x] = int(Cell.FLAG)
                        changed = True
            for y in range(cell_array.shape[0]):
                for x in range(cell_array.shape[1]):
                    if openable_array[y][x] and not no_need_to_open(cell_array, x, y):
                        board_gui_info.open_cell(x, y)
                        if cell_array[y][x] == Cell.CLOSED:
                            cell_array[y][x] = int(Cell.UNKNOWN)
                        for i in range(8):
                            d = Dir8(i)
                            if 0 <= x + d.x < cell_array.shape[1] and 0 <= y + d.y < cell_array.shape[0]:
                                if cell_array[y + d.y][x + d.x] == Cell.CLOSED:
                                    cell_array[y + d.y][x + d.x] = int(Cell.UNKNOWN)
                        changed = True

        loop_count += 1

        if not changed or util.is_key_pressed('Q'):
            break

solve(board_gui_info)