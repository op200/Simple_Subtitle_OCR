import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import easyocr
from ctypes import windll
import numpy as np
from threading import Thread
from time import sleep
from bisect import bisect_right

def error(info:str):
    print(info)

screen_width, screen_height = windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1)

path=""
scale, frame_height, frame_width, new_frame_height, new_frame_width=False,0,0,0,0
right_x,right_y,left_x,left_y = 0,0,0,0
fps, srtPath = 0, ""
difference_list = None

root_Tk = tk.Tk()
# root.geometry("300x200")
root_Tk.title("标题")


#左侧控件
left_Frame = ttk.Frame(root_Tk)
left_Frame.grid(row=0,column=0,padx=5,pady=5)
#右侧控件
right_Frame = ttk.Frame(root_Tk)
right_Frame.grid(row=0,column=1,padx=5,pady=5)


#左侧控件

#视频预览控件
video_review_Label = ttk.Label(left_Frame)
video_review_Label.grid(row=0,column=0)

#进度条控件
video_Progressbar = ttk.Progressbar(left_Frame)

frame_count = 0
frame_now = 0

#跳转当前帧
def jump_to_frame():
    global scale,frame_now,right_x,right_y,left_x,left_y,frame_count
    main_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,frame_now)
    _, frame = main_rendering_Cap.read()
    #重新绘制选框
    if scale:
        frame = cv2.resize(frame,(new_frame_width,new_frame_height))
    cv2.rectangle(frame,(right_x, right_y, left_x-right_x, left_y-right_y), color=(0,255,255),thickness=1)
    # video_review.update_idletasks()

    
    video_Progressbar["value"] = frame_now/(frame_count-1)*100

    photo = ImageTk.PhotoImage(Image.fromarray(frame))
    video_review_Label.config(image=photo)
    video_review_Label.image = photo

    #set frame_now
    frame_now_Tkvar.set(frame_now)

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

#输入路径 初始化
def submit_path(new_path):
    global path,scale,main_rendering_Cap,sec_rendering_Cap,frame_count,frame_height,frame_width,new_frame_height,new_frame_width,fps,difference_list,frame_now
    path = new_path
    #渲染控件
    frame_num_Frame.grid(row=2,column=0)

    draw_box_frame.grid(row=4,column=0,pady=15)
    ocr_set_frame.grid(row=7,column=0,pady=15)

    set_srt_Frame.grid(row=0,column=0,pady=10)

    set_ocr_Frame.grid(row=1,column=0,pady=10)

    sec_rendering_Cap = cv2.VideoCapture(path)
    main_rendering_Cap = cv2.VideoCapture(path)
    main_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,0)
    ret, frame = main_rendering_Cap.read()
    if ret:
        #获取尺寸 判断缩放
        frame_height, frame_width, _ = frame.shape
        video_size.config(text=str(frame_width)+" x "+str(frame_height))
        fps = main_rendering_Cap.get(cv2.CAP_PROP_FPS)
        video_fps.config(text=str(fps)+" FPS")
        video_size.grid(row=0,column=0)
        video_fps.grid(row=0,column=1,padx=8)
        if frame_height > screen_height*4/5 or frame_width > screen_width*4/5:
            scale = round(max(screen_height/frame_height, screen_width/frame_width)+0.5)
            new_frame_width,new_frame_height = int(frame_width/scale),int(frame_height/scale)
            frame = cv2.resize(frame,(new_frame_width,new_frame_height))
        else:
            new_frame_width,new_frame_height = frame_width,frame_height
            scale = False

        #重写进度条宽度
        video_Progressbar.config(length=new_frame_width)
        video_Progressbar.grid(row=1,column=0,pady=5)

        #渲染进度
        frame_now = 0
        jump_to_frame()

        #初始化右侧控件
        frame_count = int(main_rendering_Cap.get(cv2.CAP_PROP_FRAME_COUNT))
        difference_list = [-1]*frame_count#初始化差值表
        frame_count_Label.config(text = f" / {frame_count-1:9d}")
        frame_now_Tkvar.set(0)
        video_path_review_text = input_video_Entry.get()
        if len(video_path_review_text)>49:
            video_path_review_text = video_path_review_text[0:49]+"\n"+video_path_review_text[49:]
        if len(video_path_review_text)>99:
            video_path_review_text = video_path_review_text[0:99]+"\n"+video_path_review_text[99:]
        video_path_review_Label.config(text=video_path_review_text)


#右侧控件

#路径输入
input_video_Frame = ttk.Frame(right_Frame)
input_video_Frame.grid(row=1,column=0,pady=15)

video_path_review_Label = ttk.Label(input_video_Frame,text="输入视频路径名")
video_path_review_Label.grid(row=1,column=0,columnspan=2,pady=8)

input_video_Entry = ttk.Entry(input_video_Frame,width=40)
input_video_Entry.grid(row=2,column=0)
def enter_to_input_path(_):
    submit_path(input_video_Entry.get())
input_video_Entry.bind("<Return>", enter_to_input_path)
                
input_video_Button = ttk.Button(input_video_Frame, text="提交", width=4, command=lambda:submit_path(input_video_Entry.get()))
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

    # if frame_now == frame_count-1:
    #     video_progressbar_pos=100
    # else:
    #     video_progressbar_pos = float(frame_now)/frame_count*100

    # video_Progressbar["value"] = video_progressbar_pos
    jump_to_frame()

frame_now_Frame = ttk.Frame(frame_num_Frame)
frame_now_Frame.grid(row=0,column=0)

frame_now_Tkvar = tk.IntVar()
frame_now_Entry = ttk.Entry(frame_now_Frame,textvariable=frame_now_Tkvar,width=5)
frame_now_Entry.bind("<Return>", enter_to_change_frame_now)
frame_now_Entry.grid(row=0,column=0)

frame_count_Label = ttk.Label(frame_now_Frame,text=" / NULL")
frame_count_Label.grid(row=0,column=1)

#帧数区间
frame_range_Frame = ttk.Frame(frame_num_Frame)
frame_range_Frame.grid(row=1,column=0)

start_frame_num_Tkint = tk.IntVar()
start_frame_num_Entry = ttk.Entry(frame_range_Frame,width=11,textvariable=start_frame_num_Tkint)
set_start_frame_num_Button = ttk.Button(frame_range_Frame,text="设为开始帧",command=lambda:start_frame_num_Tkint.set(min(frame_now_Tkvar.get(),end_frame_num.get())))
start_frame_num_Entry.grid(row=0,column=0,padx=14,pady=5)
set_start_frame_num_Button.grid(row=1,column=0)

end_frame_num = tk.IntVar()
end_frame_num_entry = ttk.Entry(frame_range_Frame,width=11,textvariable=end_frame_num)
set_end_frame_num = ttk.Button(frame_range_Frame,text="设为结束帧",command=lambda:end_frame_num.set(max(frame_now_Tkvar.get(),start_frame_num_Tkint.get())))
end_frame_num_entry.grid(row=0,column=1,padx=14)
set_end_frame_num.grid(row=1,column=1)

#视频信息
video_info_frame = ttk.Frame(right_Frame)
video_info_frame.grid(row=3,column=0,pady=10)

video_size = ttk.Label(video_info_frame)
video_fps = ttk.Label(video_info_frame)

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
    global scale,right_x,right_y,left_x,left_y
    
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
    if scale:
        frame = cv2.resize(frame,(new_frame_width,new_frame_height))
    cv2.rectangle(frame,(right_x, right_y, left_x-right_x, left_y-right_y), color=(0,255,255),thickness=1)
    photo = ImageTk.PhotoImage(Image.fromarray(frame))
    video_review_Label.config(image=photo)
    video_review_Label.image = photo

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
set_srtPath_Entry.insert(0,r".\output.srt")
set_srtPath_Entry.grid(row=0,column=1)

overwrite_Tkbool = tk.BooleanVar()
overwrite_set = ttk.Checkbutton(set_srt_Frame,text="覆写SRT",var=overwrite_Tkbool)
overwrite_set.grid(row=0,column=2,padx=10)


set_ocr_Frame = ttk.Frame(output_setup_frame)

set_language_title_Label = ttk.Label(set_ocr_Frame,text="OCR语言:")
set_language_title_Label.grid(row=0,column=1)

set_language_Entry = ttk.Entry(set_ocr_Frame)
set_language_Entry.insert(0,"ch_sim,en")
set_language_Entry.grid(row=0,column=2)

open_gpu_Tkbool = tk.BooleanVar()
open_gpu_set_Button = ttk.Checkbutton(set_ocr_Frame,text="使用GPU",var=open_gpu_Tkbool)
open_gpu_set_Button.grid(row=0,column=3,padx=10)

ocr_set_frame = ttk.Frame(right_Frame)

threshold_value_input_title_Label = ttk.Label(ocr_set_frame,text="转场检测阈值:")
threshold_value_input_title_Label.grid(row=0,column=0)
threshold_value_Tkint = tk.IntVar(value=-1)
threshold_value_Entry = ttk.Entry(ocr_set_frame,width=5,textvariable=threshold_value_Tkint)
threshold_value_Entry.grid(row=0,column=1)

is_Listener_threshold_value_Entry = False
transition_frame_num_Label = ttk.Label(ocr_set_frame, text="符合阈值帧 / 总检测帧 : 0 / 0")
transition_frame_num_Label.grid(row=0,column=2)
transition_frame_num_Label.grid_forget()

start_ocr = ttk.Button(ocr_set_frame,text="开始")
start_ocr.grid(row=1,column=0,columnspan=2,pady=10)


#选框
start_x,start_y,end_x,end_y = 0,0,0,0

def draw_box():
    global scale,frame_now,start_x,start_y,end_x,end_y,right_x,right_y,left_x,left_y
    main_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,frame_now)
    _, frame = main_rendering_Cap.read()

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

def draw_down(event):
    global start_x, start_y
    start_x,start_y = event.x, event.y
video_review_Label.bind("<Button-1>", draw_down)

def draw_drag(event):
    global end_x, end_y
    end_x,end_y = event.x, event.y
    draw_box()
video_review_Label.bind("<B1-Motion>", draw_drag)




#OCR执行
class SRT:
    line_num = 0

    def __init__(self, path:str):
        try:
            f = open(path, 'w')
        except IOError:
            error("无法打开:"+path)
        else:
            if overwrite_Tkbool:
                f.write("")
            f.close()
            self.path = path
            self.line_num = 1
    
    def start_write(self):
        try:
            self.srt = open(self.path, 'a')
        except  IOError:
            error("无法打开:"+self.path)
        else:
            self.is_open = True

    def writeLine(self, start_time:float, end_time:float, line:str):
        self.srt.write(f"{self.line_num}\n{int(start_time//3600):02d}:{int(start_time%3600//60):02d}:{int(start_time%60):02d},{int(str(round(start_time%1,3))[2:]):03d} --> {int(end_time//3600):02d}:{int(end_time%3600//60):02d}:{int(end_time%60):02d},{int(str(round(end_time%1,3))[2:]):03d}\n{line}\n")
        self.line_num += 1

    def end_write(self):
        self.srt.close()
    

ocr_reader,srt = None,None
def findThreshold_start():
    global ocr_reader,srt
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
    overwrite_set.config(state=tk.DISABLED)
    set_language_Entry.config(state=tk.DISABLED)
    open_gpu_set_Button.config(state=tk.DISABLED)

    start_frame_num_Entry.config(state=tk.DISABLED)
    set_start_frame_num_Button.config(state=tk.DISABLED)
    end_frame_num_entry.config(state=tk.DISABLED)
    set_end_frame_num.config(state=tk.DISABLED)

    threshold_value_Entry.config(state=tk.DISABLED)

    start_ocr.config(text="OCR",command=start_OCR)
    start_ocr.config(state=tk.DISABLED)

    video_review_Label.unbind("<MouseWheel>")
    video_Progressbar.unbind("<MouseWheel>")
    video_Progressbar.unbind("<B1-Motion>")
    video_Progressbar.unbind("<Button-1>")
    video_review_Label.unbind("<B1-Motion>")
    video_review_Label.unbind("<Button-1>")
    findThreshold_reading()
    # findThreshold_end()



def findThreshold_end():
    global ocr_reader,srt,difference_list
    srt.end_write()

    input_video_Entry.config(state=tk.NORMAL)
    input_video_Button.config(state=tk.NORMAL)
    frame_now_Entry.config(state=tk.NORMAL)
    draw_box_right_x.config(state=tk.NORMAL)
    draw_box_right_y.config(state=tk.NORMAL)
    draw_box_left_x.config(state=tk.NORMAL)
    draw_box_left_y.config(state=tk.NORMAL)

    set_srtPath_Entry.config(state=tk.NORMAL)
    overwrite_set.config(state=tk.NORMAL)
    set_language_Entry.config(state=tk.NORMAL)
    open_gpu_set_Button.config(state=tk.NORMAL)

    start_frame_num_Entry.config(state=tk.NORMAL)
    set_start_frame_num_Button.config(state=tk.NORMAL)
    end_frame_num_entry.config(state=tk.NORMAL)
    set_end_frame_num.config(state=tk.NORMAL)

    threshold_value_Entry.config(state=tk.NORMAL)
    transition_frame_num_Label.grid_forget()

    start_ocr.config(text="开始",command=findThreshold_start)
    video_review_Label.bind("<MouseWheel>", video_progressbar_mousewheel)
    video_Progressbar.bind("<MouseWheel>", video_progressbar_mousewheel)
    video_Progressbar.bind("<B1-Motion>", video_progressbar_leftDrag)
    video_Progressbar.bind("<Button-1>", video_progressbar_leftDrag)
    video_review_Label.bind("<B1-Motion>", draw_drag)
    video_review_Label.bind("<Button-1>", draw_down)
    del srt
    del ocr_reader
    difference_list = [-1]*frame_count
    
start_ocr.config(command=findThreshold_start)

kernel = np.ones((5,5),np.uint8)
def threshold_detection(img1,img2,kernel) -> int:
    difference = cv2.absdiff(cv2.erode(cv2.erode(cv2.dilate(cv2.Canny(img1,50,240),kernel,iterations=1),kernel,iterations=1),kernel,iterations=1),cv2.erode(cv2.erode(cv2.dilate(cv2.Canny(img2,50,240),kernel,iterations=1),kernel,iterations=1),kernel,iterations=1))
    return int(cv2.sumElems(difference)[0]/difference.size*1000)


def findThreshold_reading():
    global right_x,right_y,left_x,left_y,frame_count,frame_now,start_num,end_num,bedraw_frame
    
    if left_x<4 or left_y<4:
        sec_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,0)
        _, frame = sec_rendering_Cap.read()
        left_y, left_x, _ = frame.shape

    #获取帧范围
    start_num,end_num = int(start_frame_num_Entry.get()),int(end_frame_num_entry.get())
    if start_num<0:
        start_num=0
    if end_num>frame_count-1:
        end_num=frame_count-1
    if start_num>end_num:
        start_num=end_num

    if threshold_value_Entry.get() != "0":#阈值不为0 生成差值表
        bedraw_frame = np.zeros((left_y-right_y,left_x-right_x,3),np.uint8)
        sec_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,start_num)
        frame_now = start_num
        Thread(target=Thread_compute_difference, args=(bedraw_frame,)).start()
        Thread(target=Thread_draw_video_progress).start()
        

def Thread_compute_difference(frame_front):
    global bedraw_frame,frame_now,is_Listener_threshold_value_Entry,end_num
    while frame_now<=end_num:
        _, frame = sec_rendering_Cap.read()
        frame_behind = frame[right_y:left_y, right_x:left_x]
        bedraw_frame = frame_behind
        if difference_list[frame_now]==-1:
            #写入差值
            difference_list[frame_now] = threshold_detection(frame_front, frame_behind, kernel)
            # print(difference_list[frame_now])
        #下一帧
        frame_front = frame_behind
        frame_now+=1
    frame_now-=1

    threshold_value_Entry.config(state=tk.NORMAL)

    transition_frame_num_Label.grid()
    is_Listener_threshold_value_Entry = True
    Thread(target=Listener_threshold_value_Entry).start()
    
    start_ocr.config(text="OCR",state=tk.NORMAL)


def Thread_draw_video_progress():
    # global bedraw_frame,frame_now,end_num
    global frame_now,end_num
    while True:
        if frame_now>end_num:
            sleep(0.2)
            continue

        # video_Progressbar["value"] = frame_now/(frame_count-1)*100
        jump_to_frame()

        if frame_now==end_num:
            break
        sleep(0.5)


def Listener_threshold_value_Entry():
    global difference_list,start_num,end_num,sorted_difference_list

    total_num = end_num-start_num+1
    sorted_difference_list = sorted(difference_list[start_num:end_num+1])

    while is_Listener_threshold_value_Entry:
        if len(threshold_value_Entry.get())>0:
            if threshold_value_Entry.get().isdigit() or threshold_value_Entry.get()[0] in ('-','+') and threshold_value_Entry.get()[1:].isdigit():
                transition_frame_num_Label.config(text = f"符合阈值帧 / 总检测帧 : {total_num - bisect_right(sorted_difference_list, threshold_value_Tkint.get())} / {total_num}")
        
        sleep(0.5)

def start_OCR():
    global is_Listener_threshold_value_Entry,frame_now,start_num,end_num,is_Thread_OCR_reading

    threshold_value_Entry.config(state=tk.DISABLED)
    is_Listener_threshold_value_Entry = False


    frame_now = start_num

    is_Thread_OCR_reading = True
    ocr_reading = Thread(target=Thread_OCR_reading).start()

    Thread(target=Thread_draw_video_progress).start()

    frame_now = end_num#close the Thread_draw_video_progress

    def end_OCR():
        global is_Thread_OCR_reading,frame_now
        is_Thread_OCR_reading = False
        ocr_reading.join()
        frame_now = end_num
        findThreshold_end()
    start_ocr.config(text="终止",command=end_OCR)
    

def Thread_OCR_reading():
    global frame_now

    srt.start_write()

    #第一行
    previous_line, previous_time = "", 0
    for frame_num in range(start_num,end_num+1):
        if difference_list[frame_num] > threshold_value_Tkint.get():
            frame_now = frame_num

            sec_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,frame_num)
            _, frame = sec_rendering_Cap.read()

            readed_text = ocr_reader.readtext(frame[right_y:left_y, right_x:left_x], detail=0)

            previous_line = ""
            for text in readed_text:
                previous_line += text+'\n'
                
            previous_time = frame_num/fps
            break

    #中间所有行
    current_line = ""
    for frame_num in range(frame_now+1,end_num+1):
        if not is_Thread_OCR_reading:
            return
        if difference_list[frame_num] > threshold_value_Tkint.get():
            frame_now = frame_num

            sec_rendering_Cap.set(cv2.CAP_PROP_POS_FRAMES,frame_num)
            _, frame = sec_rendering_Cap.read()

            readed_text = ocr_reader.readtext(frame[right_y:left_y, right_x:left_x], detail=0)

            current_line = ""
            for text in readed_text:
                current_line += text+'\n'

            if previous_line != current_line:
                print("writ -- :"+previous_line)
                current_time = frame_num/fps
                srt.writeLine(previous_time, current_time, previous_line)
                previous_line = current_line
                previous_time = current_time

    #最后一行
    srt.writeLine(previous_time, end_num/fps, current_line)

    srt.end_write()

    start_ocr.config(text="完成",command=findThreshold_end)

root_Tk.mainloop()