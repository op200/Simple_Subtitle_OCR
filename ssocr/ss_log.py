import ctypes
from ctypes import wintypes
import datetime
import enum
import os
import tkinter as tk


class log:
    class Level(enum.Enum):
        info = enum.auto()
        warning = enum.auto()
        error = enum.auto()

    default_foreground_color: int = 39
    default_background_color: int = 49

    @staticmethod
    def reset_cmd_color():
        if os.name == "nt":

            class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
                _fields_ = [
                    ("dwSize", wintypes._COORD),
                    ("dwCursorPosition", wintypes._COORD),
                    ("wAttributes", wintypes.WORD),
                    ("srWindow", wintypes.SMALL_RECT),
                    ("dwMaximumWindowSize", wintypes._COORD),
                ]

            csbi = CONSOLE_SCREEN_BUFFER_INFO()
            hOut = ctypes.windll.kernel32.GetStdHandle(-11)
            ctypes.windll.kernel32.FlushConsoleInputBuffer(hOut)
            ctypes.windll.kernel32.GetConsoleScreenBufferInfo(hOut, ctypes.byref(csbi))
            attributes = csbi.wAttributes
            color_map = {
                0: 0,  # 黑色
                1: 4,  # 蓝色
                2: 2,  # 绿色
                3: 6,  # 青色
                4: 1,  # 红色
                5: 5,  # 紫红色
                6: 3,  # 黄色
                7: 7,  # 白色
            }

            log.default_foreground_color = (
                30
                + color_map.get(attributes & 0x0007, 9)
                + 60 * ((attributes & 0x0008) != 0)
            )
            log.default_background_color = (
                40
                + color_map.get((attributes >> 4) & 0x0007, 9)
                + 60 * ((attributes & 0x0080) != 0)
            )

            if log.default_foreground_color == 37:
                log.default_foreground_color = 39
            if log.default_background_color == 40:
                log.default_background_color = 49

    log_Text: tk.Text | None = None

    @staticmethod
    def output(msg: object, log_level: Level):
        match log_level:
            case log.Level.info:
                color = 94 if log.default_background_color == 44 else 34
            case log.Level.warning:
                color = 93 if log.default_background_color == 43 else 33
            case log.Level.error:
                color = 91 if log.default_background_color == 41 else 31

        print(
            f"\033[{92 if log.default_background_color == 42 else 32}m{datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S.%f')[:-4]}"
            " "
            f"\033[{color}m{msg}\033[{log.default_foreground_color}m"
        )

        if log.log_Text is None:
            return
        try:
            log.log_Text.insert(tk.END, f"{msg}\n")
            log.log_Text.see(tk.END)
        except NameError:
            pass

    @staticmethod
    def info(msg: object):
        log.output(f"[INFO] {msg}", log.Level.info)

    @staticmethod
    def warning(msg: object):
        log.output(f"[WARNING] {msg}", log.Level.warning)

    @staticmethod
    def error(msg: object):
        log.output(f"[ERROR] {msg}", log.Level.error)
