import win32.win32gui as win32gui

# Windowの名前の一覧を返す(ソート済み)
def get_all_window_text() -> list:
    text_list = []
    def callback(hwnd: int, wildcard) -> None:
        text = win32gui.GetWindowText(hwnd)
        if len(text) > 0:
            text_list.append(win32gui.GetWindowText(hwnd))
    win32gui.EnumWindows(callback, None)
    text_list = list(set(text_list))
    text_list.sort()
    return text_list

def exists_window(text: str) -> bool:
    return win32gui.FindWindow(0, text) != 0

def set_foreground(text: str) -> None:
    if exists_window(text):
        hwnd = win32gui.FindWindow(0, text)
        win32gui.SetForegroundWindow(hwnd)

def try_set_minesweeper_foreground(minesweeper_window_text: str) -> None:
    windows_text_list = get_all_window_text()
    found = False
    for window_text in windows_text_list:
        if minesweeper_window_text in window_text:
            try:
                set_foreground(window_text)
                found = True
                break
            except:
                pass
    if not found:
        print(f"Error: Not Found Window '{minesweeper_window_text}'")
        exit()