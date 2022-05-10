from enum import IntEnum
import numpy as np
import ctypes

class Cell(IntEnum):
    TYPE_0 = 0
    TYPE_1 = 1
    TYPE_2 = 2
    TYPE_3 = 3
    TYPE_4 = 4
    TYPE_5 = 5
    TYPE_6 = 6
    TYPE_7 = 7
    TYPE_8 = 8
    CLOSED = 9
    FLAG = 10
    BOMB = 11
    START = 12
    UNKNOWN = 13

    def is_number(self) -> bool:
        return int(self) <= 8

    def __str__(self):
        value_to_str = [
            '0', 
            '1', #\033[36m1\033[0m', 
            '2', #'\033[32m2\033[0m', 
            '3', #'\033[31m3\033[0m', 
            '4', #'\033[34m4\033[0m',
            '5',
            '6',
            '7',
            '8',
            '.', # closed
            '|', # flag
            '@', # bomb
            's', # start
            'x'  # unknown
        ]
        return value_to_str[int(self)]

class Dir8(IntEnum):
    RN = 0
    RD = 1
    ND = 2
    LD = 3
    RU = 4
    NU = 5
    LU = 6
    LN = 7

    def reverse(self):
        return Dir8(7 - self)

    def to_numpy(self) -> np.ndarray:
        return np.array([self.x, self.y])
    
    def to_tuple(self) -> tuple[int, int]:
        return self.x, self.y
    
    @property
    def x(self) -> int:
        return [1, 1, 0, -1, 1, 0, -1, -1][int(self)]
    
    @property
    def y(self) -> int:
        return [0, 1, 1, 1, -1, -1, -1, 0][int(self)]

def is_key_pressed(key: str) -> None:
    return(bool(ctypes.windll.user32.GetAsyncKeyState(ord(key)) & 0x8000))