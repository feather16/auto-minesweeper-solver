def rgb_8bit_to_int(rgb) -> int:
    return (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]

def int_to_rgb_8bit(rgb: int) -> list[int]:
    return [rgb >> 16, (rgb >> 8) & 0xff, rgb & 0xff]