import cv2
from PIL import Image, ImageTk
import numpy as np

from threading import Thread
from time import sleep

from math import floor
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

VERSION = "0.6"

from typing import Callable
#日志
class log:
    log_level = 0

    @staticmethod
    def output(info:object, level:int=140):
        if level>log.log_level:
            print(info)

    @staticmethod
    def exit():
        log.error("program interruption")
        exit()

    @staticmethod
    def error(info:object, level:int=110):
        if level>log.log_level:
            log.output(f"\033[31m[ERROR]\033[0m {info}")

    @staticmethod
    def errore(info:object):
        log.error(info)
        log.exit()

    @staticmethod
    def warning(info:object, level:int=70):
        if level>log.log_level:
            log.output(f"\033[33m[WARNING]\033[0m {info}")

    @staticmethod
    def info(info:object, level:int=30):
        if level>log.log_level:
            log.output(f"\033[35m[INFO]\033[0m {info}")

import sys

cmds = sys.argv[1:]

for cmd in cmds:
    if cmd=="-v" or cmd=="-version":
        log.output(f"Simple Subtitle OCR (CLI)\nVersion: {VERSION}\nhttps://github.com/op200/Simple_Subtitle_OCR")
        exit()
    if cmd=="-h" or cmd=="-help":
        print("""
Simple Subtitle OCR (CLI) help:

-h/-help
    print help

-v/-version
    print version

-i/-input <string>
    input video or img sequence 's path
    default: None

-sf <int in [0:]>
    set start frame
    default: 0

-ef <int in [sf:]>
    set end frame
    this frame will be input, == [sf:ef+1] in python
    default: (the last frame of the video)

-sb <int:int:int:int>
    set select box
    x1:y1:x2:y2
    select box is [(x1, x1), (x2-1, y2-1)], == [y2:y1, x2:x1] in python
    "-sb 0:0:0:0" == "-sb 0:0:(the video's width):(the video's height)"
    default: 0:0:0:0

-srt <string>
    set the output srt's path
    default: ".\SS_OCR_CLI-output.srt"

-ow <bool>
    is it overwrite srt
    default: True

-l <string>
    set language
    if the OCR tool support plurality of language, separate each word with ','
    default: "ch"

-gpu <bool>
    is it use gpu
    default: False

-th <int>
    set the threshold value
    if th < 0, threshold detection will be skipped
    default: 0

-ocr <string>
    set OCR tool's name
    support: "paddleocr", "easyocr"
    default: "paddleocr"

-fps <float>
    force fps
    it can change the subtitle's time stamp
    default: None

-loglevel <int>
    log level
    if it > 20 , some INFO    will not be print
    if it > 40 , all  INFO    will not be print
    if it > 60 , some WARRING will not be print
    if it > 80 , all  WARRING will not be print
    if it > 100, some ERROR   will not be print
    if it > 120, all  ERROR   will not be print
    if it > 140, all  logs    will not be print
    default: 0
              """)
        exit()

input_path:str = None
start_frame:int = 0
end_frame:int = None # = the last frame of the video
select_box:tuple = (0,0,0,0)
srt_path:str = ".\SS_OCR_CLI-output.srt"
overwrite_srt:bool = True
language:tuple = ("ch",)
use_gpu:bool = False
threshold:int = 0
ocr_tool_name:str = "paddleocr"
fps_force:float = None

for i in range(len(cmds)):
    # input
    if cmds[i]=="-i" or cmds[i]=="-input":
        input_path = cmds[i+1]

    # startf
    if cmds[i]=="-sf":
        try:
            start_frame = int(cmds[i+1])
        except:
            log.errore("start frame error")

    # endf
    if cmds[i]=="-ef":
        try:
            end_frame = int(cmds[i+1])
        except:
            log.errore("end frame error")
    
    # select box
    # x1:y1:x2:y2
    if cmds[i]=="-sb":
        try:
            select_box = tuple(map(int, cmds[i+1].split(':')))
        except:
            log.errore("select box error")
        if len(select_box)!=4:
            log.errore("select box error")

    # srt path
    if cmds[i]=="-srt":
        srt_path = cmds[i+1]

    # overwrite srt
    if cmds[i]=="-ow":
        try:
            overwrite_srt = bool(int(cmds[i+1]))
        except:
            log.errore("overwrite srt option error")

    # language
    if cmds[i]=="-l":
        try:
            language = tuple(cmds[i+1].split(','))
        except:
            log.errore("language setting error")

    # use GPU
    if cmds[i]=="-gpu":
        try:
            use_gpu = bool(int(cmds[i+1]))
        except:
            log.errore("use GPU option error")

    # threshold
    if cmds[i]=="-th":
        try:
            threshold = int(cmds[i+1])
        except:
            log.errore("threshold value error")

    # force fps
    if cmds[i]=="-fps":
        try:
            fps_force = float(cmds[i+1])
        except:
            log.errore("force fps value error")

    # OCR tool
    # global ocr_tool_name
    if cmds[i]=="-ocr":
        ocr_tool_name = cmds[i+1]
        if not ocr_tool_name in ["paddleocr", "easyocr"]:
            log.errore("OCR tool name error")
    
    # log level
    if cmds[i]=="-loglevel":
        try:
            log.log_level = int(cmds[i+1])
        except:
            log.errore("log level error")

log.info("read command complete", 10)
log.info("analysis command", 8)


if not input_path:
    log.errore("none file be inputed")

# 载入视频
log.info("open video", 8)
video_cap = cv2.VideoCapture(input_path)
if not video_cap.isOpened():
    # log.errore("video can't be readed")
    pass
log.info("open video complete", 10)


video_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_count = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = fps_force if fps_force else video_cap.get(cv2.CAP_PROP_FPS)
log.info(f"video info: {video_width}x{video_height}p {frame_count}F {fps}FPS",35)

if end_frame==None:
    end_frame = frame_count-1
elif end_frame >= frame_count:
    log.errore("-ef is too large")

if end_frame<start_frame:
    log.errore("the -ef must be >= the -sf")

select_frame_num = end_frame - start_frame + 1


if select_box == (0,0,0,0):
    select_box = (0,0,video_width,video_height)
else:
    select_box = (min(select_box[0],select_box[2]),
                  min(select_box[1],select_box[3]),
                  max(select_box[0],select_box[2]),
                  max(select_box[1],select_box[3]),)

log.info("analysis command complete", 10)

# 载入OCR库
log.info("import ocr", 8)
if ocr_tool_name == "paddleocr":
    try:
        from paddleocr import PaddleOCR
    except ModuleNotFoundError:
        log.errore("from paddleocr import PaddleOCR - failed")
    ocr_choice=1
    ocr_reader = PaddleOCR(show_log=False, lang=language[0], use_gpu=use_gpu)

elif ocr_tool_name == "easyocr":
    try:
        import easyocr
    except ModuleNotFoundError:
        log.errore("import easyocr - failed")
    ocr_choice=2
    ocr_reader = easyocr.Reader(language, gpu=use_gpu)

log.info("import ocr complete", 10)


# 阈值检测
difference_list = [False]*select_frame_num # 初始化差值表
kernel = np.ones((5,5),np.uint8)
def threshold_detection(img1,img2,kernel) -> int:
    difference = cv2.absdiff(
        cv2.erode(
            cv2.erode(
                cv2.dilate(cv2.Canny(img1,50,240),kernel,iterations=1),
                kernel,iterations=1
            ),
            kernel,iterations=1
        ),
        cv2.erode(
            cv2.erode(
                cv2.dilate(cv2.Canny(img2,50,240),kernel,iterations=1),
                kernel,iterations=1
            ),
            kernel,iterations=1
        )
    )
    return int(cv2.sumElems(difference)[0]/difference.size*1000)

if threshold>=0:
    log.info("difference calculation", 8)
    frame_front = np.zeros((select_box[3]-select_box[1], select_box[2]-select_box[0], 3),np.uint8)
    video_cap.set(cv2.CAP_PROP_POS_FRAMES,start_frame)
    for frame_num in range(start_frame,end_frame+1):
        frame_behind = video_cap.read()[1][select_box[1]:select_box[3], select_box[0]:select_box[2]]

        difference_list[frame_num-start_frame] = (threshold_detection(frame_front, frame_behind, kernel) > threshold)
        
        frame_front = frame_behind

    threshold_pass_list = [i for i,v in enumerate(difference_list) if v]

    log.info("difference calculation complete", 10)

else:
    threshold_pass_list = list(range(start_frame,end_frame+1))

threshold_pass_num = len(threshold_pass_list)
log.info(f"passed / selected / total: {threshold_pass_num} / {select_frame_num} / {frame_count}")

# print all frames char preview
all_frames_preview = (
    '.'*start_frame +
    ''.join(['|' if t else '*' for t in difference_list]) +
    '.'*(frame_count-end_frame-1)
)
interval = max(round(fps),5)
log.info((lambda: "frames preview:\n" + '\n'.join([
    f"{i:>{len(str(frame_count))}} F\n" + all_frames_preview[i:i+interval]
    for i in range(0, len(all_frames_preview), interval)
]))())

# OCR, 启动!
class SRT:
    line_num = 0

    def __init__(self, path:str):
        try:
            if overwrite_srt:
                f = open(path, 'w')
            else:
                f = open(path, 'a')
        except IOError:
            log.error("can not open srt:"+path)
            log.info(f"difference_list:{difference_list}")
            log.exit()
        else:
            f.close()
            self.path = path
            self.line_num = 1
    
    def start_write(self):
        try:
            self.srt = open(self.path, 'a')
        except IOError:
            log.error("can not open srt:"+self.path)
            log.info(f"difference_list:{difference_list}")
            log.exit()

    def writeLine(self, start_time:float, end_time:float, line:str):
        start_time = floor(start_time*1000)/1000
        end_time = floor(end_time*1000)/1000
        self.srt.write(f"{self.line_num}\n{int(start_time//3600):02d}:{int(start_time%3600//60):02d}:{int(start_time%60):02d},{int(round(start_time%1*1000)):03d} --> {int(end_time//3600):02d}:{int(end_time%3600//60):02d}:{int(end_time%60):02d},{int(round(end_time%1*1000)):03d}\n{line}\n")
        self.line_num += 1

    def end_write(self):
        self.srt.close()


ocred_num:int = 0
def OCR_API(frame):
    global ocred_num,select_frame_num
    if ocr_choice==1:
        text=ocr_reader.ocr(frame)[0]
        if text==None:
            readed_text=[""]
        else:
            readed_text = [line[1][0] for line in text]
    elif ocr_choice==2:
        readed_text = ocr_reader.readtext(frame, detail=0)
    
    ocred_num+=1
    _ = f"OCR进度: {ocred_num} / {select_frame_num} = {ocred_num/select_frame_num*100:.2f}%"
    return '\n'.join(readed_text)+'\n'


log.info("OCR start", 10)
srt = SRT(srt_path)
srt.start_write()
if threshold>=0:
    # 第一行
    previous_time = threshold_pass_list[0]/fps
    
    video_cap.set(cv2.CAP_PROP_POS_FRAMES, threshold_pass_list[0])
    previous_line = OCR_API(video_cap.read()[1][select_box[1]:select_box[3], select_box[0]:select_box[2]])

    # 中间行
    for frame_num in threshold_pass_list[1:]:

        video_cap.set(cv2.CAP_PROP_POS_FRAMES,frame_num)
        current_line = OCR_API(video_cap.read()[1][select_box[1]:select_box[3], select_box[0]:select_box[2]])

        if previous_line != current_line:
            current_time = frame_num/fps
            srt.writeLine(previous_time, current_time, previous_line)
            previous_line, previous_time = current_line, current_time

    #最后一行
    srt.writeLine(previous_time, threshold_pass_list[-1]/fps, previous_line)

    srt.end_write()

else:
    # 第一行
    previous_time = start_frame/fps
    
    video_cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    previous_line = OCR_API(video_cap.read()[1][select_box[1]:select_box[3], select_box[0]:select_box[2]])

    previous_time = frame_num/fps

    # 中间行
    for frame_num in threshold_pass_list[1:]:

        current_line = OCR_API(video_cap.read()[1][select_box[1]:select_box[3], select_box[0]:select_box[2]])

        if previous_line != current_line:
            current_time = frame_num/fps
            srt.writeLine(previous_time, current_time, previous_line)
            previous_line, previous_time = current_line, current_time

    #最后一行
    srt.writeLine(previous_time, threshold_pass_list[-1]/fps, previous_line)

    srt.end_write()

        
log.info("OCR complete", 12)