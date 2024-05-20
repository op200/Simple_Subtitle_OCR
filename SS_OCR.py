import tkinter as tk
from tkinter import ttk

import cv2
from PIL import Image, ImageTk
import numpy as np

from threading import Thread
from time import sleep

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import webbrowser
def hyperlink_jump(hyperlink:str):
    webbrowser.open(hyperlink)
import shutil


VERSION = "0.4.3"

#日志
class log:
    @staticmethod
    def output(info:str):
        log_text.insert(tk.END,info+'\n')

    @staticmethod
    def error(info:str):
        log.output(f"[ERROR]{info}")

    @staticmethod
    def warning(info:str):
        log.output(f"[WARNING]{info}")

    @staticmethod
    def info(info:str):
        log.output(f"[INFO]{info}")


import platform
#判断系统对应路径
os_type = platform.system()
if os_type == 'Windows':
    config_dir = os.path.join(os.getenv('APPDATA'), 'SS_OCR')
elif os_type == 'Linux' or os_type == 'Darwin':
    config_dir = os.path.join(os.path.expanduser('~'), '.config', 'SS_OCR')
else:
    config_dir = ""
    log.warning("无法确认系统")

os.makedirs(config_dir, exist_ok=True)

ocr_choice:int = 1

import configparser
#不存在配置则写入默认配置
config = configparser.ConfigParser()
config_file_pathname = os.path.join(config_dir, 'config.ini')
if not os.path.exists(config_file_pathname) or config.read(config_file_pathname) and config.get("DEFAULT","version")!=VERSION:
    config["DEFAULT"] = {
        "version" : VERSION,
        "ocr" : "PaddleOCR",
        "language" : "ch",
        "srt_path" : r".\output.srt",
        "srt_overwrite" : 0,
        "use_gpu" : 0
    }
    with open(config_file_pathname, 'w') as configfile:
        config.write(configfile)




path=str
scale, frame_height, frame_width, new_frame_height, new_frame_width = False, int,int,int,int
right_x,right_y,left_x,left_y = 0,0,0,0
fps = int
difference_list = list
VIDEO_FRAME_IMG_HEIGHT = 6


root_Tk = tk.Tk()
root_Tk.title("Simple Subtitle OCR")


#样式
from tkinter import font as tkfont
TkDefaultFont = tkfont.nametofont("TkDefaultFont").actual()['family']
underline_font = tkfont.Font(family=TkDefaultFont, size=tkfont.nametofont("TkDefaultFont").actual()['size'], underline=True)


#菜单
menu_Menu = tk.Menu(root_Tk)

menu_setting_Menu = tk.Menu(menu_Menu, tearoff=0)
menu_setting_switchOCR_Menu = tk.Menu(menu_Menu, tearoff=0)
def switch_to_paddleocr():
    global config
    if os.path.exists(config_file_pathname):
        config["DEFAULT"]["ocr"]="PaddleOCR"
        config["DEFAULT"]["language"]="ch"
        with open(config_file_pathname, 'w') as configfile:
            config.write(configfile)
    ocr_choice = 1
    set_language_Entry.delete(0,tk.END)
    set_language_Entry.insert(0,"ch")
    log.info("切换至PaddleOCR")

def switch_to_EasyOCR():
    global config
    if os.path.exists(config_file_pathname):
        config["DEFAULT"]["ocr"]="EasyOCR"
        config["DEFAULT"]["language"]="ch_sim,en"
        with open(config_file_pathname, 'w') as configfile:
            config.write(configfile)
    ocr_choice = 2
    set_language_Entry.delete(0,tk.END)
    set_language_Entry.insert(0,"ch_sim,en")
    log.info("切换至EasyOCR")

menu_setting_switchOCR_Menu.add_command(label="PaddleOCR",command=switch_to_paddleocr)
menu_setting_switchOCR_Menu.add_command(label="EasyOCR",command=switch_to_EasyOCR)


menu_Menu.add_cascade(label="设置",menu=menu_setting_Menu)
menu_setting_Menu.add_cascade(label="切换OCR库",menu=menu_setting_switchOCR_Menu)
def remove_config_dir():
    if os.path.exists(config_dir):
        shutil.rmtree(config_dir)
        log.info("已删除"+config_dir)
    else:
        log.error("未找到配置文件目录"+config_dir)
menu_setting_Menu.add_command(label="清除配置文件",command=lambda:shutil.rmtree(config_dir))


def create_help_about_Toplevel():
    about_Toplevel = tk.Toplevel(root_Tk,width=20,height=15)
    about_Toplevel.geometry('320x180')
    about_Toplevel.title("About")
    frame = ttk.Frame(about_Toplevel)
    frame.pack(expand=True)
    ttk.Label(frame,text=f"Simple Subtitle OCR {VERSION}\n\n").pack()

    hyperlink="https://github.com/op200/Simple_Subtitle_OCR"
    hyperlink_Label = ttk.Label(frame,text=hyperlink, cursor="hand2", foreground="blue", font=underline_font)
    hyperlink_Label.bind("<Button-1>",lambda _:hyperlink_jump(hyperlink))
    hyperlink_Label.pack()
    
menu_help_Menu = tk.Menu(menu_Menu, tearoff=0)
menu_help_Menu.add_command(label="关于",command=create_help_about_Toplevel)
menu_Menu.add_cascade(label="帮助",menu=menu_help_Menu)


root_Tk.config(menu=menu_Menu)

#左侧控件
left_Frame = ttk.Frame(root_Tk, cursor="tcross")
left_Frame.grid(row=0,column=0,padx=5,pady=5)
#右侧控件
right_Frame = ttk.Frame(root_Tk)
right_Frame.grid(row=0,column=1,padx=5,pady=5)


#左侧控件

#视频预览控件
video_review_Label = ttk.Label(left_Frame, cursor="target")

#进度条控件
video_Progressbar = ttk.Progressbar(left_Frame)


def draw_video_frame_Label_frameColor(frame_num:int, color:tuple[int,int,int]):
    global video_frame_img
    x = round(new_frame_width*frame_num/(frame_count-1))-1
    if x<0:
        x=0
    video_frame_img[:VIDEO_FRAME_IMG_HEIGHT-1, x] = color

def flush_video_frame_Label():
    photo = ImageTk.PhotoImage(Image.fromarray(video_frame_img))
    video_frame_Label.config(image=photo)
    video_frame_Label.image = photo

def draw_video_frame_Label_range(start_frame:int, end_frame:int, color:tuple[int,int,int]):
    global video_frame_img
    video_frame_img[-1,:,:]=0
    video_frame_img[-1, max(round(new_frame_width*start_frame/(frame_count-1))-1, 0):max(round(new_frame_width*end_frame/(frame_count-1))-1, 0) + 1] = color


video_frame_Label = ttk.Label(left_Frame)

frame_count = 0
frame_now = 0

#跳转当前帧
def jump_to_frame():
    global scale,frame_now,frame_count
    main_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,frame_now)
    _, frame = main_rendering_Cap.read()
    try:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except cv2.error:
        log.warning(f"[{frame_now}]该帧无法读取(应检查视频封装)")
    else:
        #重新绘制选框
        if scale:
            frame = cv2.resize(frame,(new_frame_width,new_frame_height))
        cv2.rectangle(frame,(right_x, right_y, left_x-right_x, left_y-right_y), color=(0,255,255),thickness=1)

        
        video_Progressbar["value"] = frame_now/(frame_count-1)*100
        
        photo = ImageTk.PhotoImage(Image.fromarray(frame))
        video_review_Label.config(image=photo)
        video_review_Label.image = photo

        #set frame_now
        frame_now_Tkint.set(frame_now)

#进度条的滚轮事件
def video_progressbar_mousewheel(event):
    global frame_now,frame_count
    frame_now += (1 if event.delta<0 else -1)
    if frame_now<0:
        frame_now=0
    if frame_now>=frame_count:
        frame_now=frame_count-1
    
    jump_to_frame()
video_review_Label.bind("<MouseWheel>", video_progressbar_mousewheel)
video_Progressbar.bind("<MouseWheel>", video_progressbar_mousewheel)
video_frame_Label.bind("<MouseWheel>", video_progressbar_mousewheel)

#进度条鼠标点击事件
def video_progressbar_leftDrag(event):
    ratio = event.x / video_Progressbar.winfo_width()
    if ratio>1:
        ratio=1
    if ratio<0:
        ratio=0
    # video_Progressbar["value"] = ratio*100
    global frame_now,frame_count
    frame_now = int((frame_count-1)*ratio)
    jump_to_frame()
video_Progressbar.bind("<B1-Motion>", video_progressbar_leftDrag)
video_Progressbar.bind("<Button-1>", video_progressbar_leftDrag)
video_frame_Label.bind("<B1-Motion>", video_progressbar_leftDrag)
video_frame_Label.bind("<Button-1>", video_progressbar_leftDrag)

#输入路径 初始化
def submit_path(_):
    log.info("使用的OCR库是: "+config.get("DEFAULT","ocr"))

    global path,scale,main_rendering_Cap,sec_rendering_Cap,frame_count,frame_height,frame_width,new_frame_height,new_frame_width,fps,difference_list,frame_now
    path = input_video_Entry.get()
    #渲染控件
    frame_num_Frame.grid(row=2,column=0)

    draw_box_frame.grid(row=4,column=0,pady=15)
    ocr_set_Frame.grid(row=7,column=0,pady=15)

    set_srt_Frame.grid(row=0,column=0,pady=10)

    set_ocr_Frame.grid(row=1,column=0,pady=10)
    
    log_Frame.grid(row=8,column=0,pady=10)

    sec_rendering_Cap = cv2.VideoCapture(path)
    main_rendering_Cap = cv2.VideoCapture(path)
    main_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,0)
    ret, frame = main_rendering_Cap.read()
    if ret:
        #获取尺寸 判断缩放
        frame_height, frame_width, _ = frame.shape
        video_size_Label.config(text=str(frame_width)+" x "+str(frame_height))
        fps = main_rendering_Cap.get(cv2.CAP_PROP_FPS)
        video_fps_Label.config(text=str(fps)+" FPS")
        video_size_Label.grid(row=0,column=0)
        video_fps_Label.grid(row=0,column=1,padx=8)
        print(root_Tk.winfo_screenheight()*4/5,root_Tk.winfo_screenheight())
        if frame_height > root_Tk.winfo_screenheight()*4/5 or frame_width > root_Tk.winfo_screenwidth()*4/5:
            scale = max(root_Tk.winfo_screenheight()/frame_height, root_Tk.winfo_screenwidth()/(frame_width+200), 1.8)
            new_frame_width,new_frame_height = int(frame_width/scale),int(frame_height/scale)
            frame = cv2.resize(frame,(new_frame_width,new_frame_height))
            log.info(f"视频画幅过大 预览画面已缩小(1/{scale:.2f}-->{new_frame_width}x{new_frame_height})")
        else:
            new_frame_width,new_frame_height = frame_width,frame_height
            scale = False

        #重写进度条
        video_review_Label.grid(row=0,column=0,pady=5)

        video_Progressbar.config(length=new_frame_width)
        video_Progressbar.grid(row=2,column=0)


        #渲染进度
        frame_now = 0
        jump_to_frame()

        #初始化右侧控件
        frame_count = int(main_rendering_Cap.get(cv2.CAP_PROP_FRAME_COUNT))
        difference_list = [-1]*frame_count#初始化差值表
        frame_count_Label.config(text = f" / {frame_count-1:9d}")
        frame_now_Tkint.set(0)
        video_path_review_text = input_video_Entry.get()
        if len(video_path_review_text)>49:
            video_path_review_text = video_path_review_text[0:49]+"\n"+video_path_review_text[49:]
        if len(video_path_review_text)>99:
            video_path_review_text = video_path_review_text[0:99]+"\n"+video_path_review_text[99:]
        if len(video_path_review_text)>149:
            video_path_review_text = video_path_review_text[0:149]+"\n"+video_path_review_text[149:]
        video_path_review_Label.config(text=video_path_review_text)


        #绘制进度条的帧提示
        global video_frame_img
        video_frame_img = np.ones((VIDEO_FRAME_IMG_HEIGHT,new_frame_width,3), np.uint8) * 224
        video_frame_img[-1,:,:] = 1
        for frame_num in range(0,frame_count):
            draw_video_frame_Label_frameColor(frame_num, (0,0,0))
        flush_video_frame_Label()

        video_frame_Label.grid(row=3,column=0)

    else:
        log.error("无法打开"+path)
    
    root_Tk.focus_set()

#右侧控件

#路径输入
input_video_Frame = ttk.Frame(right_Frame)
input_video_Frame.grid(row=1,column=0,pady=15)

video_path_review_Label = ttk.Label(input_video_Frame,text="输入视频路径名")
video_path_review_Label.grid(row=1,column=0,columnspan=2,pady=8)

input_video_Entry = ttk.Entry(input_video_Frame,width=40)
input_video_Entry.grid(row=2,column=0)
input_video_Entry.focus_set()

input_video_Entry.bind("<Return>", submit_path)
                
input_video_Button = ttk.Button(input_video_Frame, text="提交", width=4, command=lambda:submit_path(None))
input_video_Button.grid(row=2,column=1,padx=5)

#帧数
frame_num_Frame = ttk.Frame(right_Frame)

def enter_to_change_frame_now(_):
    global frame_now,frame_count

    frame_now = int(frame_now_Entry.get())
    if frame_now<0:
        frame_now=0
    if frame_now>=frame_count:
        frame_now=frame_count-1

    jump_to_frame()
    root_Tk.focus_set()

frame_now_Frame = ttk.Frame(frame_num_Frame)
frame_now_Frame.grid(row=0,column=0)

frame_now_Tkint = tk.IntVar()
frame_now_Entry = ttk.Entry(frame_now_Frame,textvariable=frame_now_Tkint,width=5)
frame_now_Entry.bind("<Return>", enter_to_change_frame_now)
frame_now_Entry.grid(row=0,column=0)

frame_count_Label = ttk.Label(frame_now_Frame,text=" / NULL")
frame_count_Label.grid(row=0,column=1)

#帧数区间
frame_range_Frame = ttk.Frame(frame_num_Frame)
frame_range_Frame.grid(row=1,column=0)

def set_start_frame_num_Click(frame1_Tkint:tk.IntVar, frame2_Tkint:tk.IntVar):
    frame1_Tkint.set(frame_now_Tkint.get())
    if start_frame_num_Tkint.get() > end_frame_num_Tkint.get():
        frame2_Tkint.set(frame1_Tkint.get())
    draw_video_frame_Label_range(start_frame_num_Tkint.get(),end_frame_num_Tkint.get(),(228,12,109))
    flush_video_frame_Label()

start_frame_num_Tkint = tk.IntVar()
start_frame_num_Entry = ttk.Entry(frame_range_Frame,width=11,textvariable=start_frame_num_Tkint)
set_start_frame_num_Button = ttk.Button(frame_range_Frame,text="设为开始帧",command=lambda:set_start_frame_num_Click(start_frame_num_Tkint,end_frame_num_Tkint))
start_frame_num_Entry.grid(row=0,column=0,padx=14,pady=5)
set_start_frame_num_Button.grid(row=1,column=0)

end_frame_num_Tkint = tk.IntVar()
end_frame_num_Entry = ttk.Entry(frame_range_Frame,width=11,textvariable=end_frame_num_Tkint)
set_end_frame_num_Button = ttk.Button(frame_range_Frame,text="设为结束帧",command=lambda:set_start_frame_num_Click(end_frame_num_Tkint,start_frame_num_Tkint))
end_frame_num_Entry.grid(row=0,column=1,padx=14)
set_end_frame_num_Button.grid(row=1,column=1)

#视频信息
video_info_Frame = ttk.Frame(right_Frame)
video_info_Frame.grid(row=3,column=0,pady=10)

video_size_Label = ttk.Label(video_info_Frame)
video_fps_Label = ttk.Label(video_info_Frame)

#选框位置
draw_box_frame = ttk.Frame(right_Frame)

right_x_text,right_y_text,left_x_text,left_y_text = tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar()

draw_box_right_x,draw_box_right_y = ttk.Entry(draw_box_frame,textvariable=right_x_text,width=5),ttk.Entry(draw_box_frame,textvariable=right_y_text,width=5)
draw_box_left_x,draw_box_left_y = ttk.Entry(draw_box_frame,textvariable=left_x_text,width=5),ttk.Entry(draw_box_frame,textvariable=left_y_text,width=5)
draw_box_right_x.grid(row=0,column=0,padx=15)
draw_box_right_y.grid(row=0,column=1,padx=15)
draw_box_left_x.grid(row=0,column=2,padx=15)
draw_box_left_y.grid(row=0,column=3,padx=15)

def enter_to_change_draw_box(_):
    global scale,right_x,right_y,left_x,left_y,difference_list
    
    difference_list = [-1]*frame_count

    if right_x_text.get() < 0:
        right_x_text.set(0)
    if right_y_text.get() < 0:
        right_y_text.set(0)
    if left_x_text.get() >= frame_width:
        left_x_text.set(frame_width)
    if left_y_text.get() >= frame_height:
        left_y_text.set(frame_height)

    if scale:
        right_x = int(right_x_text.get()*new_frame_width/frame_width)
        right_y = int(right_y_text.get()*new_frame_width/frame_width)
        left_x = int(left_x_text.get()*new_frame_width/frame_width)
        left_y = int(left_y_text.get()*new_frame_width/frame_width)
    else:
        right_x = right_x_text.get()
        right_y = right_y_text.get()
        left_x = left_x_text.get()
        left_y = left_y_text.get()
    
    main_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,frame_now)
    _, frame = main_rendering_Cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    if scale:
        frame = cv2.resize(frame,(new_frame_width,new_frame_height))
    cv2.rectangle(frame,(right_x, right_y, left_x-right_x, left_y-right_y), color=(0,255,255),thickness=1)
    photo = ImageTk.PhotoImage(Image.fromarray(frame))
    video_review_Label.config(image=photo)
    video_review_Label.image = photo
    root_Tk.focus_set()

draw_box_right_x.bind("<Return>", enter_to_change_draw_box)
draw_box_right_y.bind("<Return>", enter_to_change_draw_box)
draw_box_left_x.bind("<Return>", enter_to_change_draw_box)
draw_box_left_y.bind("<Return>", enter_to_change_draw_box)

#输出相关控件
output_setup_frame = ttk.Frame(right_Frame)
output_setup_frame.grid(row=5,column=0)

set_srt_Frame = ttk.Frame(output_setup_frame)

set_srtPath_title = ttk.Label(set_srt_Frame,text="SRT位置:")
set_srtPath_title.grid(row=0,column=0)

set_srtPath_Entry = ttk.Entry(set_srt_Frame)
set_srtPath_Entry.insert(0,config.get("DEFAULT","srt_path"))
set_srtPath_Entry.grid(row=0,column=1)

srt_overwrite_Tkbool = tk.BooleanVar()
srt_overwrite_Tkbool.set(bool(int(config.get("DEFAULT","srt_overwrite"))))
srt_overwrite_set = ttk.Checkbutton(set_srt_Frame,text="覆写SRT",var=srt_overwrite_Tkbool)
srt_overwrite_set.grid(row=0,column=2,padx=10)


set_ocr_Frame = ttk.Frame(output_setup_frame)

set_language_title_Label = ttk.Label(set_ocr_Frame,text="OCR语言:")
set_language_title_Label.grid(row=0,column=1)

set_language_Entry = ttk.Entry(set_ocr_Frame)
set_language_Entry.insert(0,config.get("DEFAULT","language"))
set_language_Entry.grid(row=0,column=2)

open_gpu_Tkbool = tk.BooleanVar()
open_gpu_Tkbool.set(bool(int(config.get("DEFAULT","use_gpu"))))
open_gpu_set_Checkbutton = ttk.Checkbutton(set_ocr_Frame,text="使用GPU",var=open_gpu_Tkbool)
open_gpu_set_Checkbutton.grid(row=0,column=3,padx=10)


ocr_set_Frame = ttk.Frame(right_Frame)


threshold_value_input_Frame = ttk.Frame(ocr_set_Frame)
threshold_value_input_Frame.grid(row=0,column=0)

threshold_value_input_title_Label = ttk.Label(threshold_value_input_Frame,text="转场检测阈值:")
threshold_value_input_title_Label.grid(row=0,column=0)
threshold_value_input_Tkint = tk.IntVar(value=-1)
threshold_value_input_Entry = ttk.Entry(threshold_value_input_Frame,width=5,textvariable=threshold_value_input_Tkint)
threshold_value_input_Entry.grid(row=0,column=1)


start_threshold_detection_Frame = tk.Frame(ocr_set_Frame)
start_threshold_detection_Frame.grid(row=1,column=0,pady=15)

start_threshold_detection_Button = ttk.Button(start_threshold_detection_Frame,text="阈值检测")
start_threshold_detection_Button.grid(row=0,column=0,padx=15)

restart_threshold_detection_Button = ttk.Button(start_threshold_detection_Frame,text="重新检测")
restart_threshold_detection_Button.grid(row=0,column=1,padx=15)


is_Listener_threshold_value_Entry = False
transition_frame_num_Label = ttk.Label(ocr_set_Frame, text="符合阈值帧 / 总检测帧 : 0 / 0")
transition_frame_num_Label.grid(row=2,column=0)
transition_frame_num_Label.grid_forget()

now_frame_Dvalue_Label = ttk.Label(ocr_set_Frame, text="当前帧差值: ")
now_frame_Dvalue_Label.grid(row=3,column=0)
now_frame_Dvalue_Label.grid_forget()



log_Frame = ttk.Frame(right_Frame)

log_vScrollbar = ttk.Scrollbar(log_Frame)
log_vScrollbar.grid(row=0,column=1,sticky='ns')

log_text = tk.Text(log_Frame,width=45,height=10, yscrollcommand=log_vScrollbar.set)
log_text.grid(row=0,column=0,sticky='nsew')


log_vScrollbar.config(command=log_text.yview)
#读取配置
config.read(config_file_pathname)
if config.get("DEFAULT","ocr") == "PaddleOCR":
    ocr_choice = 1
    try:
        from paddleocr import PaddleOCR
    except ModuleNotFoundError:
        log.error("未能载入库:paddleocr")
elif config.get("DEFAULT","ocr") == "EasyOCR":
    ocr_choice = 2
    try:
        import easyocr
    except ModuleNotFoundError:
        log.error("未能载入库:easyocr")



#选框
start_x,start_y,end_x,end_y = 0,0,0,0

def draw_box():
    global scale,frame_now,start_x,start_y,end_x,end_y,right_x,right_y,left_x,left_y
    main_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,frame_now)
    _, frame = main_rendering_Cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    right_x = min(start_x,end_x)
    right_y = min(start_y,end_y)
    left_x = max(start_x,end_x)
    left_y = max(start_y,end_y)

    if right_x < 0:
        right_x = 0
    if right_y < 0:
        right_y = 0
    if left_x >= video_review_Label.winfo_width()-4:
        left_x = video_review_Label.winfo_width()-4
    if left_y >= video_review_Label.winfo_height()-4:
        left_y = video_review_Label.winfo_height()-4
    if scale:
        frame = cv2.resize(frame,(new_frame_width,new_frame_height))
    cv2.rectangle(frame,(right_x, right_y, left_x-right_x, left_y-right_y), color=(0,255,255),thickness=1)

    if scale:
        right_x_text.set(int(right_x*frame_width/new_frame_width))
        right_y_text.set(int(right_y*frame_width/new_frame_width))
        left_x_text.set(int(left_x*frame_width/new_frame_width))
        left_y_text.set(int(left_y*frame_width/new_frame_width))
    else:
        right_x_text.set(right_x)
        right_y_text.set(right_y)
        left_x_text.set(left_x)
        left_y_text.set(left_y)

    photo = ImageTk.PhotoImage(Image.fromarray(frame))
    video_review_Label.config(image=photo)
    video_review_Label.image = photo

def draw_video_review_MouseDown(event):
    global start_x, start_y
    start_x,start_y = event.x, event.y
video_review_Label.bind("<Button-1>", draw_video_review_MouseDown)

def draw_video_review_MouseDrag(event):
    global end_x, end_y
    end_x,end_y = event.x, event.y
    draw_box()
video_review_Label.bind("<B1-Motion>", draw_video_review_MouseDrag)




#OCR执行
class SRT:
    line_num = 0

    def __init__(self, path:str):
        try:
            f = open(path, 'w')
        except IOError:
            log.error("无法打开:"+path)
        else:
            if srt_overwrite_Tkbool:
                f.write("")
            f.close()
            self.path = path
            self.line_num = 1
    
    def start_write(self):
        try:
            self.srt = open(self.path, 'a')
        except  IOError:
            log.error("无法打开:"+self.path)
        else:
            self.is_open = True

    def writeLine(self, start_time:float, end_time:float, line:str):
        self.srt.write(f"{self.line_num}\n{int(start_time//3600):02d}:{int(start_time%3600//60):02d}:{int(start_time%60):02d},{int(round(start_time%1*1000)):03d} --> {int(end_time//3600):02d}:{int(end_time%3600//60):02d}:{int(end_time%60):02d},{int(round(end_time%1*1000)):03d}\n{line}\n")
        self.line_num += 1

    def end_write(self):
        self.srt.close()
    

ocr_reader,srt = None,None
def findThreshold_start():

    #保存配置
    config["DEFAULT"]["language"] = set_language_Entry.get()
    config["DEFAULT"]["srt_path"] = set_srtPath_Entry.get()
    config["DEFAULT"]["srt_overwrite"] = str(1 if srt_overwrite_Tkbool.get() else 0)
    config["DEFAULT"]["use_gpu"] = str(1 if open_gpu_Tkbool.get() else 0)
	
    with open(config_file_pathname, 'w') as configfile:
        config.write(configfile)

    global ocr_reader,srt
    if ocr_choice==1:
        ocr_reader = PaddleOCR(lang=set_language_Entry.get(),use_gpu=open_gpu_Tkbool.get())
    elif ocr_choice==2:
        ocr_reader = easyocr.Reader(set_language_Entry.get().split(','),gpu=open_gpu_Tkbool.get())
    
    srt = SRT(set_srtPath_Entry.get())
    input_video_Entry.config(state=tk.DISABLED)
    input_video_Button.config(state=tk.DISABLED)
    frame_now_Entry.config(state=tk.DISABLED)
    draw_box_right_x.config(state=tk.DISABLED)
    draw_box_right_y.config(state=tk.DISABLED)
    draw_box_left_x.config(state=tk.DISABLED)
    draw_box_left_y.config(state=tk.DISABLED)

    set_srtPath_Entry.config(state=tk.DISABLED)
    srt_overwrite_set.config(state=tk.DISABLED)
    set_language_Entry.config(state=tk.DISABLED)
    open_gpu_set_Checkbutton.config(state=tk.DISABLED)

    start_frame_num_Entry.config(state=tk.DISABLED)
    set_start_frame_num_Button.config(state=tk.DISABLED)
    end_frame_num_Entry.config(state=tk.DISABLED)
    set_end_frame_num_Button.config(state=tk.DISABLED)

    threshold_value_input_Entry.config(state=tk.DISABLED)

    start_threshold_detection_Button.config(text="OCR",command=start_OCR)
    start_threshold_detection_Button.config(state=tk.DISABLED)

    
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
    global ocr_reader,srt,is_Listener_threshold_value_Entry
    if hasattr(srt, 'srt'):
        srt.end_write()

    is_Listener_threshold_value_Entry=False

    input_video_Entry.config(state=tk.NORMAL)
    input_video_Button.config(state=tk.NORMAL)
    frame_now_Entry.config(state=tk.NORMAL)
    draw_box_right_x.config(state=tk.NORMAL)
    draw_box_right_y.config(state=tk.NORMAL)
    draw_box_left_x.config(state=tk.NORMAL)
    draw_box_left_y.config(state=tk.NORMAL)

    set_srtPath_Entry.config(state=tk.NORMAL)
    srt_overwrite_set.config(state=tk.NORMAL)
    set_language_Entry.config(state=tk.NORMAL)
    open_gpu_set_Checkbutton.config(state=tk.NORMAL)

    start_frame_num_Entry.config(state=tk.NORMAL)
    set_start_frame_num_Button.config(state=tk.NORMAL)
    end_frame_num_Entry.config(state=tk.NORMAL)
    set_end_frame_num_Button.config(state=tk.NORMAL)

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

    start_threshold_detection_Button.config(text="阈值检测",command=findThreshold_start)

    del srt
    del ocr_reader



start_threshold_detection_Button.config(command=findThreshold_start)
restart_threshold_detection_Button.config(command=findThreshold_end)


kernel = np.ones((5,5),np.uint8)
def threshold_detection(img1,img2,kernel) -> int:
    difference = cv2.absdiff(cv2.erode(cv2.erode(cv2.dilate(cv2.Canny(img1,50,240),kernel,iterations=1),kernel,iterations=1),kernel,iterations=1),cv2.erode(cv2.erode(cv2.dilate(cv2.Canny(img2,50,240),kernel,iterations=1),kernel,iterations=1),kernel,iterations=1))
    return int(cv2.sumElems(difference)[0]/difference.size*1000)


def findThreshold_reading():
    global frame_count,frame_now,start_num,end_num,bedraw_frame
    
    video_review_Label.bind("<MouseWheel>", video_progressbar_mousewheel)
    video_review_Label.bind("<B1-Motion>", draw_video_review_MouseDrag)
    video_review_Label.bind("<Button-1>", draw_video_review_MouseDown)

    video_Progressbar.bind("<MouseWheel>", video_progressbar_mousewheel)
    video_Progressbar.bind("<B1-Motion>", video_progressbar_leftDrag)
    video_Progressbar.bind("<Button-1>", video_progressbar_leftDrag)

    video_frame_Label.bind("<B1-Motion>", video_progressbar_leftDrag)
    video_frame_Label.bind("<Button-1>", video_progressbar_leftDrag)
    video_frame_Label.bind("<MouseWheel>", video_progressbar_mousewheel)

    if left_x_text.get()<4 or left_y_text.get()<4:
        # sec_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,0)
        # _, frame = sec_rendering_Cap.read()
        left_x_text.set(frame_width)
        left_y_text.set(frame_height)
        right_x_text.set(0)
        right_y_text.set(0)

    #获取帧范围
    start_num,end_num = int(start_frame_num_Entry.get()),int(end_frame_num_Entry.get())
    if start_num<0:
        start_num=0
    if end_num>frame_count-1:
        end_num=frame_count-1
    if start_num>end_num:
        start_num=end_num
    draw_video_frame_Label_range(start_num, end_num, (27, 241, 255))
    flush_video_frame_Label()

    if threshold_value_input_Entry.get() != "0":#阈值不为0 生成差值表
        bedraw_frame = np.zeros((left_y_text.get()-right_y_text.get(), left_x_text.get()-right_x_text.get(), 3),np.uint8)
        sec_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,start_num)
        frame_now = start_num
        Thread(target=Thread_compute_difference, args=(bedraw_frame,)).start()
        Thread(target=Thread_draw_video_progress).start()
        

def Thread_compute_difference(frame_front):
    global bedraw_frame,frame_now,is_Listener_threshold_value_Entry
    while frame_now<=end_num:
        _, frame = sec_rendering_Cap.read()
        frame_behind = frame[right_y_text.get():left_y_text.get(), right_x_text.get():left_x_text.get()]
        bedraw_frame = frame_behind
        if difference_list[frame_now]==-1:
            #写入差值
            difference_list[frame_now] = threshold_detection(frame_front, frame_behind, kernel)
        #下一帧
        frame_front = frame_behind
        frame_now+=1
    frame_now-=1

    threshold_value_input_Entry.config(state=tk.NORMAL)

    transition_frame_num_Label.grid()
    now_frame_Dvalue_Label.grid()
    is_Listener_threshold_value_Entry = True
    Thread(target=Listener_threshold_value_Entry).start()
    
    start_threshold_detection_Button.config(text="OCR",state=tk.NORMAL)


def Thread_draw_video_progress():
    # global bedraw_frame,frame_now,end_num
    global frame_now,end_num,scale,right_x,right_y,left_x,left_y
    while True:
        if frame_now>end_num:
            sleep(0.2)
            continue

        if scale:
            right_x = int(right_x_text.get()*new_frame_width/frame_width)
            right_y = int(right_y_text.get()*new_frame_width/frame_width)
            left_x = int(left_x_text.get()*new_frame_width/frame_width)
            left_y = int(left_y_text.get()*new_frame_width/frame_width)
        else:
            right_x = right_x_text.get()
            right_y = right_y_text.get()
            left_x = left_x_text.get()
            left_y = left_y_text.get()
        
        jump_to_frame()

        if frame_now==end_num:
            break
        sleep(0.5)


def Listener_threshold_value_Entry():

    total_frame_num = end_num-start_num+1

    while is_Listener_threshold_value_Entry:
        if len(threshold_value_input_Entry.get())>0:
            if threshold_value_input_Entry.get().isdigit() or threshold_value_input_Entry.get()[0] in ('-','+') and threshold_value_input_Entry.get()[1:].isdigit():
                for frame_num in range(0,frame_count):
                    draw_video_frame_Label_frameColor(frame_num, (0,0,0))

                meet_frame_num = 0
                for frame_num in range(start_num,end_num+1):
                    if difference_list[frame_num] > threshold_value_input_Tkint.get():
                        meet_frame_num += 1
                        draw_video_frame_Label_frameColor(frame_num, (237,16,234))

                flush_video_frame_Label()
                transition_frame_num_Label.config(text = f"符合阈值帧 / 总检测帧 : {meet_frame_num} / {total_frame_num}")
                now_frame_Dvalue_Label.config(text = f"当前帧差值: {difference_list[frame_now]}", foreground=('#ED10EA' if difference_list[frame_now]>threshold_value_input_Tkint.get() else 'black'))
        sleep(0.5)

def start_OCR():
    global is_Listener_threshold_value_Entry,frame_now,start_num,end_num,is_Thread_OCR_reading

    threshold_value_input_Entry.config(state=tk.DISABLED)
    is_Listener_threshold_value_Entry = False


    frame_now = start_num

    is_Thread_OCR_reading = True
    ocr_reading = Thread(target=Thread_OCR_reading)
    ocr_reading.start()

    Thread(target=Thread_draw_video_progress).start()

    frame_now = end_num#close the Thread_draw_video_progress

    def end_OCR():
        global is_Thread_OCR_reading,frame_now
        is_Thread_OCR_reading = False
        ocr_reading.join()
        frame_now = end_num
        findThreshold_end()
    start_threshold_detection_Button.config(text="终止",command=end_OCR)
    
def OCR_API(frame):
    if ocr_choice==1:
        text=ocr_reader.ocr(frame)[0]
        if text==None:
            readed_text=[""]
        else:
            readed_text = [line[1][0] for line in text]
    elif ocr_choice==2:
        readed_text = ocr_reader.readtext(frame, detail=0)

    return '\n'.join(readed_text)+'\n'

def Thread_OCR_reading():
    global frame_now

    srt.start_write()

    #第一行
    previous_line, previous_time = "", 0
    for frame_num in range(start_num,end_num+1):
        if difference_list[frame_num] > threshold_value_input_Tkint.get():
            frame_now = frame_num

            sec_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,frame_num)
            previous_line = OCR_API(sec_rendering_Cap.read()[1][right_y:left_y, right_x:left_x])
                
            previous_time = frame_num/fps
            break

    #中间所有行
    for frame_num in range(frame_now+1,end_num+1):
        if not is_Thread_OCR_reading:
            return
        if difference_list[frame_num] > threshold_value_input_Tkint.get():
            frame_now = frame_num

            sec_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,frame_num)
            current_line = OCR_API(sec_rendering_Cap.read()[1][right_y:left_y, right_x:left_x])

            if previous_line != current_line:
                current_time = frame_num/fps
                srt.writeLine(previous_time, current_time, previous_line)
                print(previous_time, current_time)
                previous_line, previous_time = current_line, current_time

    #最后一行
    srt.writeLine(previous_time, end_num/fps, current_line)

    srt.end_write()

    start_threshold_detection_Button.config(text="完成",command=findThreshold_end)

root_Tk.mainloop()