import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from math import floor
from threading import Thread
import time
import os
import shutil
import webbrowser

import cv2
from PIL import Image, ImageTk
import numpy as np

import ss_info
from ss_log import log
import ss_ocr
import ss_gui_var
from ss_config import config_dir, config_file_pathname, config, save_config
import ss_utils


def run_gui():
    ss_gui_var.root_Tk.mainloop()


path: str
scale: float | None = False
frame_height: int
frame_width: int
new_frame_height: int
new_frame_width: int

right_x: int
right_y: int
left_x: int
left_y: int
right_x = right_y = left_x = left_y = 0
fps: float
difference_list: list[int]
VIDEO_FRAME_IMG_HEIGHT = 6


ss_gui_var.root_Tk.title(ss_info.PROJECT_FULL_NAME)


def root_Tk_Close():
    save_config()
    ss_gui_var.root_Tk.destroy()


ss_gui_var.root_Tk.protocol("WM_DELETE_WINDOW", root_Tk_Close)


# 样式

TkDefaultFont = tkfont.nametofont("TkDefaultFont").actual()["family"]
underline_font = tkfont.Font(
    family=TkDefaultFont,
    size=tkfont.nametofont("TkDefaultFont").actual()["size"],
    underline=True,
)


# 菜单
menu_Menu = tk.Menu(ss_gui_var.root_Tk)

menu_setting_Menu = tk.Menu(menu_Menu, tearoff=0)
menu_setting_switchOCR_Menu = tk.Menu(menu_Menu, tearoff=0)


def switch_to_paddleocr():
    global config

    if os.path.exists(config_file_pathname):
        config["DEFAULT"]["ocr"] = ss_ocr.ocr_module.PaddleOCR.value
        config["DEFAULT"]["language"] = "ch"
        with open(config_file_pathname, "w") as configfile:
            config.write(configfile)

    set_language_Entry.delete(0, tk.END)
    set_language_Entry.insert(0, "ch")

    ss_ocr.api.switch_ocr_module(ss_ocr.ocr_module.PaddleOCR)
    log.info(f"切换至 {ss_ocr.ocr_module.PaddleOCR.value}")


def switch_to_EasyOCR():
    global config

    if os.path.exists(config_file_pathname):
        config["DEFAULT"]["ocr"] = ss_ocr.ocr_module.EasyOCR.value
        config["DEFAULT"]["language"] = "ch_sim,en"
        with open(config_file_pathname, "w") as configfile:
            config.write(configfile)

    set_language_Entry.delete(0, tk.END)
    set_language_Entry.insert(0, "ch_sim,en")

    ss_ocr.api.switch_ocr_module(ss_ocr.ocr_module.EasyOCR)
    log.info(f"切换至 {ss_ocr.ocr_module.EasyOCR.value}")

def switch_to_WeChatOCR():
    global config
    if os.path.exists(config_file_pathname):
        config["DEFAULT"]["ocr"] = ss_ocr.ocr_module.WeChatOCR.value
        config["DEFAULT"]["language"] = "ch_sim,en"
        with open(config_file_pathname, "w") as configfile:
            config.write(configfile)
    set_language_Entry.delete(0, tk.END)
    set_language_Entry.insert(0, "ch_sim,en")
    ss_ocr.api.switch_ocr_module(ss_ocr.ocr_module.WeChatOCR)
    log.info(f"切换至 {ss_ocr.ocr_module.WeChatOCR.value}")

menu_setting_switchOCR_Menu.add_command(
    label=ss_ocr.ocr_module.PaddleOCR.value, command=switch_to_paddleocr
)
menu_setting_switchOCR_Menu.add_command(
    label=ss_ocr.ocr_module.EasyOCR.value, command=switch_to_EasyOCR
)
menu_setting_switchOCR_Menu.add_command(
    label=ss_ocr.ocr_module.WeChatOCR.value, command=switch_to_WeChatOCR
)

menu_Menu.add_cascade(label="设置", menu=menu_setting_Menu)
menu_setting_Menu.add_cascade(label="切换OCR库", menu=menu_setting_switchOCR_Menu)


def remove_config_dir():
    if os.path.exists(config_dir):
        shutil.rmtree(config_dir)
        log.info("已删除" + config_dir)
    else:
        log.error("未找到配置文件目录" + config_dir)


menu_setting_Menu.add_command(label="清除配置文件", command=remove_config_dir)


def create_help_about_Toplevel():
    about_Toplevel = tk.Toplevel(ss_gui_var.root_Tk, width=20, height=15)
    about_Toplevel.geometry("320x160")
    about_Toplevel.title("About")
    frame = ttk.Frame(about_Toplevel)
    frame.pack(expand=True)
    ttk.Label(
        frame, text=f"{ss_info.PROJECT_FULL_NAME}  v{ss_info.PROJECT_VERSION}\n\n"
    ).pack()

    hyperlink_Label = ttk.Label(
        frame,
        text=ss_info.PROJECT_HOME_LINK,
        cursor="hand2",
        foreground="blue",
        font=underline_font,
    )
    hyperlink_Label.bind(
        "<Button-1>", lambda _: webbrowser.open(ss_info.PROJECT_HOME_LINK)
    )
    hyperlink_Label.pack()


menu_help_Menu = tk.Menu(menu_Menu, tearoff=0)
menu_help_Menu.add_command(label="关于", command=create_help_about_Toplevel)
menu_Menu.add_cascade(label="帮助", menu=menu_help_Menu)


ss_gui_var.root_Tk.config(menu=menu_Menu)

# 左侧控件
left_Frame = ttk.Frame(ss_gui_var.root_Tk, cursor="tcross")
left_Frame.grid(row=0, column=0, padx=5, pady=5)
# 右侧控件
right_Frame = ttk.Frame(ss_gui_var.root_Tk)
right_Frame.grid(row=0, column=1, padx=5, pady=5)


# 左侧控件

# 视频预览控件
video_review_Label = ttk.Label(left_Frame, cursor="target")

# 进度条控件
video_Progressbar = ttk.Progressbar(left_Frame)


def draw_video_frame_Label_frameColor(frame_num: int, color: tuple[int, int, int]):
    global video_frame_img
    x = round(new_frame_width * frame_num / (frame_count - 1)) - 1
    if x < 0:
        x = 0
    video_frame_img[: VIDEO_FRAME_IMG_HEIGHT - 1, x] = color


def flush_video_frame_Label():
    photo = ImageTk.PhotoImage(Image.fromarray(video_frame_img))
    video_frame_Label.config(image=photo)
    video_frame_Label.image = photo  # type: ignore


def draw_video_frame_Label_range(
    start_frame: int, end_frame: int, color: tuple[int, int, int]
):
    global video_frame_img
    video_frame_img[-1, :, :] = 0
    video_frame_img[
        -1,
        max(round(new_frame_width * start_frame / (frame_count - 1)) - 1, 0) : max(
            round(new_frame_width * end_frame / (frame_count - 1)) - 1, 0
        )
        + 1,
    ] = color


# 关键帧位置提示控件
video_frame_Label = ttk.Label(left_Frame)

frame_count = 0
frame_now = 0


def img_filter(frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
    tolerance = ss_gui_var.retain_color_tolerance_Tkint.get()
    color1 = tuple(
        int(retain_color1_Entry.get().lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
    )
    color2 = tuple(
        int(retain_color2_Entry.get().lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
    )
    # 定义颜色上下界
    lower1 = np.array(
        [
            max(0, (color1[0] - tolerance)),
            max(0, (color1[1] - tolerance)),
            max(0, (color1[2] - tolerance)),
        ]
    )
    upper1 = np.array(
        [
            min(255, (color1[0] + tolerance)),
            min(255, (color1[1] + tolerance)),
            min(255, (color1[2] + tolerance)),
        ]
    )

    lower2 = np.array(
        [
            max(0, (color2[0] - tolerance)),
            max(0, (color2[1] - tolerance)),
            max(0, (color2[2] - tolerance)),
        ]
    )
    upper2 = np.array(
        [
            min(255, (color2[0] + tolerance)),
            min(255, (color2[1] + tolerance)),
            min(255, (color2[2] + tolerance)),
        ]
    )
    # 创建掩码
    mask1 = cv2.inRange(frame, lower1, upper1)
    mask2 = cv2.inRange(frame, lower2, upper2)
    # 合并掩码
    mask = cv2.bitwise_or(mask1, mask2)
    mask = cv2.bitwise_not(mask)

    purple = (142, 12, 255)
    frame[mask > 0] = purple

    return frame


def jump_to_frame(frame_new: int | None):
    """
    预览画面跳转到指定帧

    int 为指定帧, None 为 frame_now
    """

    global scale, frame_now, frame_count

    frame: cv2.typing.MatLike

    if frame_new is not None and frame_new == frame_now + 1:
        frame = preview_Cap.read()[1]
    elif frame_new == frame_now:
        return
    else:
        if frame_new is None:
            frame_new = frame_now
        preview_Cap.set(cv2.CAP_PROP_POS_FRAMES, frame_new)
        frame = preview_Cap.read()[1]

    frame_now = frame_new

    try:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except cv2.error:
        log.warning(f"[{frame_now}]该帧无法读取(应检查视频封装)")
    else:
        if ss_gui_var.set_filter_Tkbool.get():
            frame = img_filter(frame)
        # 重新绘制选框
        if scale:
            frame = cv2.resize(frame, (new_frame_width, new_frame_height))
        cv2.rectangle(
            frame,
            (right_x, right_y, left_x - right_x, left_y - right_y),
            color=(0, 255, 255),
            thickness=1,
        )

        video_Progressbar["value"] = frame_now / (frame_count - 1) * 100

        photo = ImageTk.PhotoImage(Image.fromarray(frame))
        video_review_Label.config(image=photo)
        video_review_Label.image = photo  # type: ignore

        # set frame_now
        frame_now_Tkint.set(frame_now)


# 进度条的滚轮事件
def video_progressbar_mousewheel(event):
    global frame_now, frame_count

    frame_new = frame_now

    frame_new += 1 if event.delta < 0 else -1
    if frame_new < 0:
        frame_new = 0
    if frame_new >= frame_count:
        frame_new = frame_count - 1

    jump_to_frame(frame_new)


video_review_Label.bind("<MouseWheel>", video_progressbar_mousewheel)
video_Progressbar.bind("<MouseWheel>", video_progressbar_mousewheel)
video_frame_Label.bind("<MouseWheel>", video_progressbar_mousewheel)


# 进度条鼠标点击事件
def video_progressbar_leftDrag(event):
    ratio = event.x / video_Progressbar.winfo_width()
    if ratio > 1:
        ratio = 1
    if ratio < 0:
        ratio = 0
    global frame_count
    jump_to_frame(int((frame_count - 1) * ratio))


video_Progressbar.bind("<B1-Motion>", video_progressbar_leftDrag)
video_Progressbar.bind("<Button-1>", video_progressbar_leftDrag)
video_frame_Label.bind("<B1-Motion>", video_progressbar_leftDrag)
video_frame_Label.bind("<Button-1>", video_progressbar_leftDrag)


# 输入路径 初始化
def submit_path(_):
    log.info("使用的OCR库是: " + config.get("DEFAULT", "ocr"))

    global \
        path, \
        scale, \
        preview_Cap, \
        sec_rendering_Cap, \
        frame_count, \
        frame_height, \
        frame_width, \
        new_frame_height, \
        new_frame_width, \
        fps, \
        difference_list, \
        frame_now
    path = input_video_Entry.get()
    path = path.strip('"')
    # 渲染控件
    frame_num_Frame.grid(row=2, column=0)

    draw_box_Frame.grid(row=4, column=0, pady=15)
    set_filter_Frame.grid(row=6, column=0)
    ocr_set_Frame.grid(row=7, column=0, pady=15)

    set_srt_Frame.grid(row=0, column=0, pady=10)

    set_ocr_Frame.grid(row=1, column=0, pady=10)

    log_Frame.grid(row=8, column=0, pady=10)

    sec_rendering_Cap = cv2.VideoCapture(path)
    preview_Cap = cv2.VideoCapture(path)
    preview_Cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    ret, frame = preview_Cap.read()
    if ret:
        # 获取尺寸 判断缩放
        frame_height, frame_width, _ = frame.shape
        video_size_Label.config(text=str(frame_width) + " x " + str(frame_height))
        fps = preview_Cap.get(cv2.CAP_PROP_FPS)
        video_fps_Label.config(text=str(fps) + " FPS")
        video_size_Label.grid(row=0, column=0)
        video_fps_Label.grid(row=0, column=1, padx=8)
        if (
            frame_height > ss_gui_var.root_Tk.winfo_screenheight() * 5 / 6
            or frame_width > ss_gui_var.root_Tk.winfo_screenwidth() * 4 / 5
        ):
            scale = max(
                (1.2 * frame_height + 100) / ss_gui_var.root_Tk.winfo_screenheight(),
                (1.2 * frame_width + 500) / ss_gui_var.root_Tk.winfo_screenwidth(),
                1.5,
            )
            new_frame_width, new_frame_height = (
                int(frame_width / scale),
                int(frame_height / scale),
            )
            frame = cv2.resize(frame, (new_frame_width, new_frame_height))
            log.info(
                f"视频画幅过大 预览画面已缩小(1/{scale:.2f}-->{new_frame_width}x{new_frame_height})"
            )
        else:
            new_frame_width, new_frame_height = frame_width, frame_height
            scale = None

        # 重写进度条
        video_review_Label.grid(row=0, column=0, pady=5)

        video_Progressbar.config(length=new_frame_width)
        video_Progressbar.grid(row=2, column=0)

        # 渲染进度
        jump_to_frame(None)

        # 初始化右侧控件
        frame_count = int(preview_Cap.get(cv2.CAP_PROP_FRAME_COUNT))
        difference_list = [-1] * frame_count  # 初始化差值表
        frame_count_Label.config(text=f" / {frame_count - 1:9d}")
        frame_now_Tkint.set(0)
        video_path_review_text = input_video_Entry.get()
        if len(video_path_review_text) > 49:
            video_path_review_text = (
                video_path_review_text[0:49] + "\n" + video_path_review_text[49:]
            )
        if len(video_path_review_text) > 99:
            video_path_review_text = (
                video_path_review_text[0:99] + "\n" + video_path_review_text[99:]
            )
        if len(video_path_review_text) > 149:
            video_path_review_text = (
                video_path_review_text[0:149] + "\n" + video_path_review_text[149:]
            )
        video_path_review_Label.config(text=video_path_review_text)

        # 绘制进度条的帧提示
        global video_frame_img
        video_frame_img = (
            np.ones((VIDEO_FRAME_IMG_HEIGHT, new_frame_width, 3), np.uint8) * 224
        )
        video_frame_img[-1, :, :] = 1
        for frame_num in range(0, frame_count):
            draw_video_frame_Label_frameColor(frame_num, (0, 0, 0))
        flush_video_frame_Label()

        video_frame_Label.grid(row=3, column=0)

    else:
        log.error("无法打开视频" + path)

    try:
        retain_color1_preview_Canvas.create_rectangle(
            -40, -40, 40, 40, fill=retain_color1_Entry.get()
        )
        retain_color2_preview_Canvas.create_rectangle(
            -40, -40, 40, 40, fill=retain_color2_Entry.get()
        )
    except Exception:
        log.error("颜色格式错误")

    ss_gui_var.root_Tk.focus_set()


# 右侧控件

# 路径输入
input_video_Frame = ttk.Frame(right_Frame)
input_video_Frame.grid(row=1, column=0, pady=15)

video_path_review_Label = ttk.Label(
    input_video_Frame,
    text="输入视频路径名",
    width=50,
    anchor="center",
    wraplength=350 * ss_gui_var.windows_scaling,
)
video_path_review_Label.grid(row=1, column=0, columnspan=2, pady=8)

input_video_Entry = ttk.Entry(input_video_Frame, width=40)
input_video_Entry.grid(row=2, column=0)
input_video_Entry.focus_set()

input_video_Entry.bind("<Return>", submit_path)

input_video_Button = ttk.Button(
    input_video_Frame, text="提交", width=4, command=lambda: submit_path(None)
)
input_video_Button.grid(row=2, column=1, padx=5)

# 帧数
frame_num_Frame = ttk.Frame(right_Frame)


def enter_to_change_frame_now(_):
    global frame_count

    frame_new = int(frame_now_Entry.get())
    if frame_new < 0:
        frame_new = 0
    if frame_new >= frame_count:
        frame_new = frame_count - 1

    jump_to_frame(frame_new)
    ss_gui_var.root_Tk.focus_set()


frame_now_Frame = ttk.Frame(frame_num_Frame)
frame_now_Frame.grid(row=0, column=0)

frame_now_Tkint = tk.IntVar()
frame_now_Entry = ttk.Entry(frame_now_Frame, textvariable=frame_now_Tkint, width=5)
frame_now_Entry.bind("<Return>", enter_to_change_frame_now)
frame_now_Entry.grid(row=0, column=0)

frame_count_Label = ttk.Label(frame_now_Frame, text=" / NULL")
frame_count_Label.grid(row=0, column=1)

# 帧数区间
frame_range_Frame = ttk.Frame(frame_num_Frame)
frame_range_Frame.grid(row=1, column=0)


def set_start_frame_num_Click(
    frame1_Tkint: tk.IntVar, frame2_Tkint: tk.IntVar, flush_frame_now: int | None = None
):
    if flush_frame_now is not None:
        jump_to_frame(flush_frame_now)

    frame1_Tkint.set(frame_now_Tkint.get())
    if start_frame_num_Tkint.get() > end_frame_num_Tkint.get():
        frame2_Tkint.set(frame1_Tkint.get())
    draw_video_frame_Label_range(
        start_frame_num_Tkint.get(), end_frame_num_Tkint.get(), (228, 12, 109)
    )
    flush_video_frame_Label()


start_frame_num_Tkint = tk.IntVar()
start_frame_num_Entry = ttk.Entry(
    frame_range_Frame, width=11, textvariable=start_frame_num_Tkint
)
start_frame_num_Entry.bind(
    "<Return>",
    lambda _: set_start_frame_num_Click(
        start_frame_num_Tkint, end_frame_num_Tkint, start_frame_num_Tkint.get()
    ),
)
set_start_frame_num_Button = ttk.Button(
    frame_range_Frame,
    text="设为开始帧",
    command=lambda: set_start_frame_num_Click(
        start_frame_num_Tkint, end_frame_num_Tkint
    ),
)
start_frame_num_Entry.grid(row=0, column=0, padx=14, pady=5)
set_start_frame_num_Button.grid(row=1, column=0)

end_frame_num_Tkint = tk.IntVar()
end_frame_num_Entry = ttk.Entry(
    frame_range_Frame, width=11, textvariable=end_frame_num_Tkint
)
end_frame_num_Entry.bind(
    "<Return>",
    lambda _: set_start_frame_num_Click(
        end_frame_num_Tkint, start_frame_num_Tkint, end_frame_num_Tkint.get()
    ),
)
set_end_frame_num_Button = ttk.Button(
    frame_range_Frame,
    text="设为结束帧",
    command=lambda: set_start_frame_num_Click(
        end_frame_num_Tkint, start_frame_num_Tkint
    ),
)
end_frame_num_Entry.grid(row=0, column=1, padx=14)
set_end_frame_num_Button.grid(row=1, column=1)

# 视频信息
video_info_Frame = ttk.Frame(right_Frame)
video_info_Frame.grid(row=3, column=0, pady=10)

video_size_Label = ttk.Label(video_info_Frame)
video_fps_Label = ttk.Label(video_info_Frame)

# 选框位置
draw_box_Frame = ttk.Frame(right_Frame)

left_x_Tkint, left_y_Tkint, right_x_Tkint, right_y_Tkint = (
    tk.IntVar(),
    tk.IntVar(),
    tk.IntVar(),
    tk.IntVar(),
)

draw_box_left_x, draw_box_left_y = (
    ttk.Entry(draw_box_Frame, textvariable=left_x_Tkint, width=5),
    ttk.Entry(draw_box_Frame, textvariable=left_y_Tkint, width=5),
)
draw_box_right_x, draw_box_right_y = (
    ttk.Entry(draw_box_Frame, textvariable=right_x_Tkint, width=5),
    ttk.Entry(draw_box_Frame, textvariable=right_y_Tkint, width=5),
)
draw_box_left_x.grid(row=0, column=0, padx=15)
draw_box_left_y.grid(row=0, column=1, padx=15)
draw_box_right_x.grid(row=0, column=2, padx=15)
draw_box_right_y.grid(row=0, column=3, padx=15)


def enter_to_change_draw_box(_):
    global scale, left_x, left_y, right_x, right_y, difference_list

    difference_list = [-1] * frame_count

    lx, ly, rx, ry = (
        max(left_x_Tkint.get(), 0),
        max(left_y_Tkint.get(), 0),
        max(right_x_Tkint.get(), 0),
        max(right_y_Tkint.get(), 0),
    )

    if rx >= frame_width:
        rx = frame_width
    if ry >= frame_height:
        ry = frame_height

    if not lx == rx == ly == ry == 0:
        if lx == rx:
            rx = lx + 1
        if ly == ry:
            ry = ly + 1

    if lx > rx:
        lx, rx = rx, lx
    if ly > ry:
        ly, ry = ry, ly

    left_x_Tkint.set(lx)
    right_x_Tkint.set(rx)
    left_y_Tkint.set(ly)
    right_y_Tkint.set(ry)

    if scale:
        right_x = int(lx * new_frame_width / frame_width)
        right_y = int(ly * new_frame_width / frame_width)
        left_x = int(rx * new_frame_width / frame_width)
        left_y = int(ry * new_frame_width / frame_width)
    else:
        right_x = lx
        right_y = ly
        left_x = rx
        left_y = ry

    jump_to_frame(None)


draw_box_left_x.bind("<Return>", enter_to_change_draw_box)
draw_box_left_y.bind("<Return>", enter_to_change_draw_box)
draw_box_right_x.bind("<Return>", enter_to_change_draw_box)
draw_box_right_y.bind("<Return>", enter_to_change_draw_box)

# 输出相关控件
output_setup_Frame = ttk.Frame(right_Frame)
output_setup_Frame.grid(row=5, column=0)

set_srt_Frame = ttk.Frame(output_setup_Frame)

set_srtPath_Label = ttk.Label(set_srt_Frame, text="SRT位置:")
set_srtPath_Label.grid(row=0, column=0)

set_srtPath_Entry = ttk.Entry(set_srt_Frame, textvariable=ss_gui_var.set_srtPath_Tkstr)
set_srtPath_Entry.insert(0, config.get("DEFAULT", "srt_path"))
set_srtPath_Entry.grid(row=0, column=1)

srt_overwrite_Checkbutton = ttk.Checkbutton(
    set_srt_Frame, text="覆写SRT", variable=ss_gui_var.srt_overwrite_Tkbool
)
srt_overwrite_Checkbutton.grid(row=0, column=2, padx=10)


set_ocr_Frame = ttk.Frame(output_setup_Frame)

set_language_title_Label = ttk.Label(set_ocr_Frame, text="OCR语言:")
set_language_title_Label.grid(row=0, column=1)

set_language_Entry = ttk.Entry(
    set_ocr_Frame, textvariable=ss_gui_var.set_language_Tkstr
)
set_language_Entry.insert(0, config.get("DEFAULT", "language"))
set_language_Entry.grid(row=0, column=2)

open_gpu_set_Checkbutton = ttk.Checkbutton(
    set_ocr_Frame, text="使用GPU", variable=ss_gui_var.open_gpu_Tkbool
)
open_gpu_set_Checkbutton.grid(row=0, column=3, padx=10)


# filter相关控件
set_filter_Frame = ttk.Frame(right_Frame)


def set_filter_set_event():
    if ss_gui_var.set_filter_Tkbool.get():
        retain_color_tolerance_Entry.config(state=tk.NORMAL)
        retain_color1_Entry.config(state=tk.NORMAL)
        retain_color2_Entry.config(state=tk.NORMAL)
    else:
        retain_color_tolerance_Entry.config(state=tk.DISABLED)
        retain_color1_Entry.config(state=tk.DISABLED)
        retain_color2_Entry.config(state=tk.DISABLED)
    jump_to_frame(None)


set_filter_set = ttk.Checkbutton(
    set_filter_Frame,
    text="启用滤镜",
    variable=ss_gui_var.set_filter_Tkbool,
    command=set_filter_set_event,
)
set_filter_set.grid(row=0, column=0)

retain_color_tolerance_Frame = ttk.Frame(set_filter_Frame)
retain_color_tolerance_Frame.grid(row=0, column=1, padx=5)
retain_color_tolerance_Label = ttk.Label(retain_color_tolerance_Frame, text="容差")
retain_color_tolerance_Label.grid(row=0, column=0)

retain_color_tolerance_Entry = ttk.Entry(
    retain_color_tolerance_Frame,
    textvariable=ss_gui_var.retain_color_tolerance_Tkint,
    width=4,
)
retain_color_tolerance_Entry.grid(row=0, column=1)
retain_color_tolerance_Entry.bind("<Return>", lambda _: jump_to_frame(None))

set_color_Frame = ttk.Frame(set_filter_Frame)
set_color_Frame.grid(row=0, column=2)

retain_color1_preview_Canvas = tk.Canvas(
    set_color_Frame,
    width=10,
    height=10,
    borderwidth=0,
    highlightthickness=1,
    highlightbackground="gray",
)
retain_color1_preview_Canvas.grid(row=0, column=0, padx=5)

retain_color1_Entry = ttk.Entry(
    set_color_Frame, width=8, textvariable=ss_gui_var.retain_color1_Tkstr
)
retain_color1_Entry.grid(row=0, column=1)

retain_color2_preview_Canvas = tk.Canvas(
    set_color_Frame,
    width=10,
    height=10,
    borderwidth=0,
    highlightthickness=1,
    highlightbackground="gray",
)
retain_color2_preview_Canvas.grid(row=0, column=2, padx=5)

retain_color2_Entry = ttk.Entry(
    set_color_Frame, width=8, textvariable=ss_gui_var.retain_color2_Tkstr
)
retain_color2_Entry.grid(row=0, column=3)

if ss_gui_var.set_filter_Tkbool.get():
    retain_color_tolerance_Entry.config(state=tk.NORMAL)
    retain_color1_Entry.config(state=tk.NORMAL)
    retain_color2_Entry.config(state=tk.NORMAL)
else:
    retain_color_tolerance_Entry.config(state=tk.DISABLED)
    retain_color1_Entry.config(state=tk.DISABLED)
    retain_color2_Entry.config(state=tk.DISABLED)


def enter_to_draw_retain_color(_):
    try:
        retain_color1_preview_Canvas.create_rectangle(
            -40, -40, 40, 40, fill=retain_color1_Entry.get()
        )
        retain_color2_preview_Canvas.create_rectangle(
            -40, -40, 40, 40, fill=retain_color2_Entry.get()
        )
    except Exception:
        log.error("颜色格式错误")
    jump_to_frame(None)


retain_color1_Entry.bind("<Return>", enter_to_draw_retain_color)
retain_color2_Entry.bind("<Return>", enter_to_draw_retain_color)


ocr_set_Frame = ttk.Frame(right_Frame)


threshold_value_input_Frame = ttk.Frame(ocr_set_Frame)
threshold_value_input_Frame.grid(row=0, column=0)

threshold_value_input_title_Label = ttk.Label(
    threshold_value_input_Frame, text="转场检测阈值:"
)
threshold_value_input_title_Label.grid(row=0, column=0)
threshold_value_input_Tkint = tk.IntVar(value=-2)
threshold_value_input_Entry = ttk.Entry(
    threshold_value_input_Frame, width=5, textvariable=threshold_value_input_Tkint
)
threshold_value_input_Entry.grid(row=0, column=1)


start_threshold_detection_Frame = tk.Frame(ocr_set_Frame)
start_threshold_detection_Frame.grid(row=1, column=0, pady=15)

start_threshold_detection_Button = ttk.Button(
    start_threshold_detection_Frame, text="阈值检测"
)
start_threshold_detection_Button.grid(row=0, column=0, padx=15)

restart_threshold_detection_Button = ttk.Button(
    start_threshold_detection_Frame, text="重新检测"
)
restart_threshold_detection_Button.grid(row=0, column=1, padx=15)


is_Listener_threshold_value_Entry = False
transition_frame_num_Label = ttk.Label(
    ocr_set_Frame, text="符合阈值帧 / 总检测帧 : 0 / 0"
)
transition_frame_num_Label.grid(row=2, column=0)
transition_frame_num_Label.grid_forget()

now_frame_Dvalue_Label = ttk.Label(ocr_set_Frame, text="当前帧差值: ")
now_frame_Dvalue_Label.grid(row=3, column=0)
now_frame_Dvalue_Label.grid_forget()


log_Frame = ttk.Frame(right_Frame)

log_vScrollbar = ttk.Scrollbar(log_Frame)
log_vScrollbar.grid(row=0, column=1, sticky="ns")

log_Text = tk.Text(log_Frame, width=45, height=10, yscrollcommand=log_vScrollbar.set)  # noqa: F811
log_Text.grid(row=0, column=0, sticky="nsew")
log.log_Text = log_Text


log_vScrollbar.config(command=log.log_Text.yview)

# 读取配置
config.read(config_file_pathname)

match config.get("DEFAULT", "ocr"):
    case ss_ocr.ocr_module.PaddleOCR.value:
        ss_ocr.api.switch_ocr_module(ss_ocr.ocr_module.PaddleOCR)

    case ss_ocr.ocr_module.EasyOCR.value:
        ss_ocr.api.switch_ocr_module(ss_ocr.ocr_module.EasyOCR)

    case ss_ocr.ocr_module.WeChatOCR.value:
        ss_ocr.api.switch_ocr_module(ss_ocr.ocr_module.WeChatOCR)
    case _ as s:
        log.warning(f"未知库选项: {s}, 默认使用 {ss_ocr.ocr_module.PaddleOCR.value}")
        ss_ocr.api.switch_ocr_module(ss_ocr.ocr_module.PaddleOCR)


# 选框
start_x, start_y, end_x, end_y = 0, 0, 0, 0


def draw_box():
    global \
        scale, \
        frame_now, \
        start_x, \
        start_y, \
        end_x, \
        end_y, \
        right_x, \
        right_y, \
        left_x, \
        left_y

    right_x = min(start_x, end_x)
    right_y = min(start_y, end_y)
    left_x = max(start_x, end_x)
    left_y = max(start_y, end_y)

    if left_x == right_x:
        right_x = left_x + 1
    if left_y == right_y:
        right_y = left_y + 1

    if right_x < 0:
        right_x = 0
    if right_y < 0:
        right_y = 0

    if left_x >= (w := video_review_Label.winfo_width() - 4):
        left_x = w
    if left_y >= (h := video_review_Label.winfo_height() - 4):
        left_y = h

    if scale:
        left_x_Tkint.set(int(right_x * frame_width / new_frame_width))
        left_y_Tkint.set(int(right_y * frame_width / new_frame_width))
        right_x_Tkint.set(int(left_x * frame_width / new_frame_width))
        right_y_Tkint.set(int(left_y * frame_width / new_frame_width))
    else:
        left_x_Tkint.set(right_x)
        left_y_Tkint.set(right_y)
        right_x_Tkint.set(left_x)
        right_y_Tkint.set(left_y)

    jump_to_frame(None)


def draw_video_review_MouseDown(event):
    global start_x, start_y
    start_x, start_y = event.x, event.y


video_review_Label.bind("<Button-1>", draw_video_review_MouseDown)


def draw_video_review_MouseDrag(event):
    global end_x, end_y
    end_x, end_y = event.x, event.y
    draw_box()


video_review_Label.bind("<B1-Motion>", draw_video_review_MouseDrag)


# OCR执行


class SRT:
    line_num = 0
    # half_frame_time:float

    def __init__(self, path: str):
        try:
            if ss_gui_var.srt_overwrite_Tkbool.get():
                f = open(path, "w")
            else:
                if os.path.exists(path):
                    log.warning("已存在同名 SRT, 新的内容将在其末尾追加")
                f = open(path, "a")
        except IOError:
            log.error("无法打开: " + path)
        else:
            f.close()
            self.path = path
            self.line_num = 1
        # self.half_frame_time = 1/fps

    def start_write(self):
        try:
            self.srt = open(self.path, "a")
        except IOError:
            log.error("无法打开: " + self.path)
        else:
            self.is_open = True

    def writeLine(self, start_time: float, end_time: float, line: str):
        line = line.strip()
        if line:
            start_time = floor(start_time * 1000) / 1000
            end_time = floor(end_time * 1000) / 1000
            self.srt.write(
                f"{self.line_num}\n{int(start_time // 3600):02d}:{int(start_time % 3600 // 60):02d}:{int(start_time % 60):02d},{int(round(start_time % 1 * 1000)):03d} --> {int(end_time // 3600):02d}:{int(end_time % 3600 // 60):02d}:{int(end_time % 60):02d},{int(round(end_time % 1 * 1000)):03d}\n{line}\n\n"
            )
            self.line_num += 1

    def end_write(self):
        self.srt.close()


def findThreshold_start():
    global end_all_thread, difference_list
    end_all_thread = False

    difference_list = [-1] * frame_count
    # 这里的想的是重新检测时可以防止二次检测，但没考虑到选框改变的情况，所以暂时选择在重新检测时重置list

    save_config()

    global ocr_reader, srt

    srt = SRT(set_srtPath_Entry.get())
    input_video_Entry.config(state=tk.DISABLED)
    input_video_Button.config(state=tk.DISABLED)
    frame_now_Entry.config(state=tk.DISABLED)
    draw_box_left_x.config(state=tk.DISABLED)
    draw_box_left_y.config(state=tk.DISABLED)
    draw_box_right_x.config(state=tk.DISABLED)
    draw_box_right_y.config(state=tk.DISABLED)

    set_srtPath_Entry.config(state=tk.DISABLED)
    srt_overwrite_Checkbutton.config(state=tk.DISABLED)
    set_language_Entry.config(state=tk.DISABLED)
    open_gpu_set_Checkbutton.config(state=tk.DISABLED)

    set_filter_set.config(state=tk.DISABLED)
    retain_color_tolerance_Label.config(state=tk.DISABLED)
    retain_color_tolerance_Entry.config(state=tk.DISABLED)
    retain_color1_Entry.config(state=tk.DISABLED)
    retain_color2_Entry.config(state=tk.DISABLED)

    start_frame_num_Entry.config(state=tk.DISABLED)
    set_start_frame_num_Button.config(state=tk.DISABLED)
    end_frame_num_Entry.config(state=tk.DISABLED)
    set_end_frame_num_Button.config(state=tk.DISABLED)

    threshold_value_input_Entry.config(state=tk.DISABLED)

    start_threshold_detection_Button.config(
        state=tk.DISABLED, text="OCR", command=start_OCR
    )

    video_review_Label.unbind("<MouseWheel>")
    video_review_Label.unbind("<B1-Motion>")
    video_review_Label.unbind("<Button-1>")

    video_Progressbar.unbind("<MouseWheel>")
    video_Progressbar.unbind("<B1-Motion>")
    video_Progressbar.unbind("<Button-1>")

    video_frame_Label.unbind("<MouseWheel>")
    video_frame_Label.unbind("<B1-Motion>")
    video_frame_Label.unbind("<Button-1>")

    findThreshold_reading()


def findThreshold_end():
    global srt, is_Listener_threshold_value_Entry, frame_now, end_all_thread

    end_all_thread = True
    frame_now = end_num  # 关闭阈值检测和绘制线程
    is_Listener_threshold_value_Entry = False  # 关闭监听

    input_video_Entry.config(state=tk.NORMAL)
    input_video_Button.config(state=tk.NORMAL)
    frame_now_Entry.config(state=tk.NORMAL)
    draw_box_left_x.config(state=tk.NORMAL)
    draw_box_left_y.config(state=tk.NORMAL)
    draw_box_right_x.config(state=tk.NORMAL)
    draw_box_right_y.config(state=tk.NORMAL)

    set_srtPath_Entry.config(state=tk.NORMAL)
    srt_overwrite_Checkbutton.config(state=tk.NORMAL)
    set_language_Entry.config(state=tk.NORMAL)
    open_gpu_set_Checkbutton.config(state=tk.NORMAL)

    set_filter_set.config(state=tk.NORMAL)
    retain_color_tolerance_Label.config(state=tk.NORMAL)
    retain_color_tolerance_Entry.config(state=tk.NORMAL)
    retain_color1_Entry.config(state=tk.NORMAL)
    retain_color2_Entry.config(state=tk.NORMAL)

    start_frame_num_Entry.config(state=tk.NORMAL)
    set_start_frame_num_Button.config(state=tk.NORMAL)
    end_frame_num_Entry.config(state=tk.NORMAL)
    set_end_frame_num_Button.config(state=tk.NORMAL)

    restart_threshold_detection_Button.config(state=tk.NORMAL)

    threshold_value_input_Entry.config(state=tk.NORMAL)
    transition_frame_num_Label.grid_forget()
    now_frame_Dvalue_Label.grid_forget()

    video_review_Label.bind("<MouseWheel>", video_progressbar_mousewheel)
    video_review_Label.bind("<B1-Motion>", draw_video_review_MouseDrag)
    video_review_Label.bind("<Button-1>", draw_video_review_MouseDown)

    video_Progressbar.bind("<MouseWheel>", video_progressbar_mousewheel)
    video_Progressbar.bind("<B1-Motion>", video_progressbar_leftDrag)
    video_Progressbar.bind("<Button-1>", video_progressbar_leftDrag)

    video_frame_Label.bind("<B1-Motion>", video_progressbar_leftDrag)
    video_frame_Label.bind("<Button-1>", video_progressbar_leftDrag)
    video_frame_Label.bind("<MouseWheel>", video_progressbar_mousewheel)

    start_threshold_detection_Button.config(
        text="阈值检测", command=findThreshold_start, state=tk.NORMAL
    )

    if "srt" in globals():
        if hasattr(srt, "srt"):
            srt.end_write()
        del srt


start_threshold_detection_Button.config(command=findThreshold_start)
restart_threshold_detection_Button.config(command=findThreshold_end)


def findThreshold_reading():
    # global frame_count,frame_now,start_num,end_num,bedraw_frame
    global frame_count, frame_now, start_num, end_num

    if right_x_Tkint.get() < 4 or right_y_Tkint.get() < 4:
        # sec_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,0)
        # _, frame = sec_rendering_Cap.read()
        right_x_Tkint.set(frame_width)
        right_y_Tkint.set(frame_height)
        left_x_Tkint.set(0)
        left_y_Tkint.set(0)

    # 获取帧范围
    start_num, end_num = (
        int(start_frame_num_Entry.get()),
        int(end_frame_num_Entry.get()),
    )
    if start_num < 0:
        start_num = 0
    if end_num > frame_count - 1:
        end_num = frame_count - 1
    if start_num > end_num:
        start_num = end_num
    draw_video_frame_Label_range(start_num, end_num, (27, 241, 255))
    flush_video_frame_Label()

    # if threshold_value_input_Entry.get() != "0":#阈值不为0 生成差值表
    sec_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES, start_num)
    frame_now = start_num
    Thread(
        target=Thread_compute_difference,
        args=(
            np.zeros(
                (
                    right_y_Tkint.get() - left_y_Tkint.get(),
                    right_x_Tkint.get() - left_x_Tkint.get(),
                    3,
                ),
                np.uint8,
            ),
        ),
        daemon=True,
    ).start()
    Thread(target=Thread_draw_video_progress, daemon=True).start()


@ss_utils.timer("阈值检测")
def Thread_compute_difference(frame_front: cv2.typing.MatLike):
    global frame_now, is_Listener_threshold_value_Entry

    if threshold_value_input_Tkint.get() >= -1:
        while frame_now <= end_num:
            frame = sec_rendering_Cap.read()[1][
                left_y_Tkint.get() : right_y_Tkint.get(),
                left_x_Tkint.get() : right_x_Tkint.get(),
            ]
            frame_behind = img_filter(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if difference_list[frame_now] == -1:
                # 写入差值
                difference_list[frame_now] = ss_ocr.api.threshold_detection(
                    frame_front, frame_behind
                )
            # 下一帧
            frame_front = frame_behind
            frame_now += 1
    else:
        log.info(f"因阈值设定 {threshold_value_input_Tkint.get()} < -1, 跳过阈值检测")

    frame_now = end_num

    threshold_value_input_Entry.config(state=tk.NORMAL)

    if not end_all_thread:
        transition_frame_num_Label.grid()
        now_frame_Dvalue_Label.grid()
        is_Listener_threshold_value_Entry = True
        Thread(target=Listener_threshold_value_Entry, daemon=True).start()

        start_threshold_detection_Button.config(state=tk.NORMAL)

        video_review_Label.bind("<MouseWheel>", video_progressbar_mousewheel)
        video_review_Label.bind("<B1-Motion>", draw_video_review_MouseDrag)
        video_review_Label.bind("<Button-1>", draw_video_review_MouseDown)

        video_Progressbar.bind("<MouseWheel>", video_progressbar_mousewheel)
        video_Progressbar.bind("<B1-Motion>", video_progressbar_leftDrag)
        video_Progressbar.bind("<Button-1>", video_progressbar_leftDrag)

        video_frame_Label.bind("<B1-Motion>", video_progressbar_leftDrag)
        video_frame_Label.bind("<Button-1>", video_progressbar_leftDrag)
        video_frame_Label.bind("<MouseWheel>", video_progressbar_mousewheel)


def Thread_draw_video_progress():
    # global bedraw_frame,frame_now,end_num
    global frame_now, end_num, scale, right_x, right_y, left_x, left_y
    while not end_all_thread:
        if frame_now > end_num:
            time.sleep(0.2)
            continue

        if scale:
            right_x = int(left_x_Tkint.get() * new_frame_width / frame_width)
            right_y = int(left_y_Tkint.get() * new_frame_width / frame_width)
            left_x = int(right_x_Tkint.get() * new_frame_width / frame_width)
            left_y = int(right_y_Tkint.get() * new_frame_width / frame_width)
        else:
            right_x = left_x_Tkint.get()
            right_y = left_y_Tkint.get()
            left_x = right_x_Tkint.get()
            left_y = right_y_Tkint.get()

        jump_to_frame(None)

        if frame_now == end_num:
            break
        time.sleep(2)


def Listener_threshold_value_Entry():
    global meet_frame_num
    total_frame_num = end_num - start_num + 1

    while is_Listener_threshold_value_Entry:
        if len(threshold_value_input_Entry.get()) > 0:
            if (
                threshold_value_input_Entry.get().isdigit()
                or threshold_value_input_Entry.get()[0] in ("-", "+")
                and threshold_value_input_Entry.get()[1:].isdigit()
            ):
                for frame_num in range(0, frame_count):
                    draw_video_frame_Label_frameColor(frame_num, (0, 0, 0))

                meet_frame_num = 0
                for frame_num in range(start_num, end_num + 1):
                    if difference_list[frame_num] > threshold_value_input_Tkint.get():
                        meet_frame_num += 1
                        draw_video_frame_Label_frameColor(frame_num, (237, 16, 234))

                flush_video_frame_Label()
                transition_frame_num_Label.config(
                    text=f"符合阈值帧 / 总检测帧 : {meet_frame_num} / {total_frame_num}"
                )
                now_frame_Dvalue_Label.config(
                    text=f"当前帧差值: {difference_list[frame_now]}",
                    foreground=(
                        "#ED10EA"
                        if difference_list[frame_now]
                        > threshold_value_input_Tkint.get()
                        else "black"
                    ),
                )
        time.sleep(0.5)


def start_OCR():
    global \
        is_Listener_threshold_value_Entry, \
        frame_now, \
        start_num, \
        end_num, \
        is_Thread_OCR_reading

    restart_threshold_detection_Button.config(state=tk.DISABLED)
    threshold_value_input_Entry.config(state=tk.DISABLED)
    is_Listener_threshold_value_Entry = False

    frame_now = start_num

    ss_ocr.api.switch_ocr_module(ss_ocr.api.ocr_choice)

    is_Thread_OCR_reading = True
    ocr_reading = Thread(target=Thread_OCR_reading, daemon=True)
    ocr_reading.start()

    Thread(target=Thread_draw_video_progress, daemon=True).start()

    def end_OCR():
        global is_Thread_OCR_reading, frame_now
        is_Thread_OCR_reading = False
        ocr_reading.join()
        findThreshold_end()

    start_threshold_detection_Button.config(
        text="终止", command=lambda: Thread(target=end_OCR, daemon=True).start()
    )


def OCR_API(frame: cv2.typing.MatLike) -> str:
    global ocred_num

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = img_filter(frame)

    res_text = ss_ocr.api.ocr(frame)

    ocred_num += 1
    now_frame_Dvalue_Label.config(
        text=f"OCR进度: {ocred_num} / {meet_frame_num} = {ocred_num / meet_frame_num * 100:.2f}%"
    )
    return res_text


@ss_utils.timer("OCR")
def Thread_OCR_reading():
    global frame_now, ocred_num

    srt.start_write()
    ocred_num = 0
    now_frame_Dvalue_Label.config(foreground=("#ED10EA"))

    # 第一行
    previous_line: str | None = None
    previous_time: float | None = None
    previous_ocr_frame_num: int = -1
    for frame_num in range(start_num, end_num + 1):
        if not is_Thread_OCR_reading:
            srt.end_write()
            return
        if difference_list[frame_num] > threshold_value_input_Tkint.get():
            frame_now = frame_num

            if frame_num != previous_ocr_frame_num + 1:
                sec_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

            previous_line = OCR_API(
                sec_rendering_Cap.read()[1][
                    left_y_Tkint.get() : right_y_Tkint.get(),
                    left_x_Tkint.get() : right_x_Tkint.get(),
                ]
            )
            previous_ocr_frame_num = frame_num

            previous_time = frame_num / fps
            break

    if previous_line is None:
        log.error("第一行内容读取错误")
        previous_line = ""
    if previous_time is None:
        log.error("第一行时间读取错误")
        previous_time = 0

    current_line: str | None = None
    # 中间所有行
    for frame_num in range(frame_now + 1, end_num + 1):
        if not is_Thread_OCR_reading:
            srt.end_write()
            return
        if difference_list[frame_num] > threshold_value_input_Tkint.get():
            frame_now = frame_num

            if frame_num != previous_ocr_frame_num + 1:
                sec_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

            current_line = OCR_API(
                sec_rendering_Cap.read()[1][
                    left_y_Tkint.get() : right_y_Tkint.get(),
                    left_x_Tkint.get() : right_x_Tkint.get(),
                ]
            )
            previous_ocr_frame_num = frame_num

            if previous_line != current_line:
                current_time = frame_num / fps
                srt.writeLine(previous_time, current_time, previous_line)
                previous_line, previous_time = current_line, current_time

    # 最后一行
    if not current_line:
        current_line = previous_line
    srt.writeLine(previous_time, end_num / fps, current_line)

    srt.end_write()

    start_threshold_detection_Button.config(text="完成", command=findThreshold_end)
