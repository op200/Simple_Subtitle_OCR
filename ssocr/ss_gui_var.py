import ctypes
import os
import tkinter as tk


from ss_log import log

windows_scaling: float = 1
if os.name == "nt":
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        log.warning("Windows DPI Aware failed")

    try:
        # 获取系统 DPI 缩放比例（默认 96 DPI 是 100%）
        user32 = ctypes.windll.user32
        hdc = user32.GetDC(0)
        LOGPIXELSX = 88  # 表示水平 DPI
        windows_scaling = ctypes.windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSX) / 96.0
        user32.ReleaseDC(0, hdc)
    except Exception:
        log.warning("Get Windows scaling failed")


root_Tk = tk.Tk()

set_language_Tkstr = tk.StringVar()

open_gpu_Tkbool = tk.BooleanVar()

set_srtPath_Tkstr = tk.StringVar()

srt_overwrite_Tkbool = tk.BooleanVar()

set_filter_Tkbool = tk.BooleanVar()

retain_color_tolerance_Tkint = tk.IntVar()


retain_color1_Tkstr = tk.StringVar()
retain_color2_Tkstr = tk.StringVar()
