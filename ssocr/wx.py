import os
import re
import sys
import json
import time
from wechat_ocr.ocr_manager import OcrManager, OCR_MAX_TASK_ID
from PIL import Image
from pathlib import Path

class WxOCR:
    """WxOCR类"""
    # 假设微信安装在默认的路径下
    common_paths = ""
    #common_paths = r"C:\\Program Files (x86)\\Tencent\WeChat"
    ramdisk = ""
    #ramdisk = "L:/"
    wechat_dir = ""
    wechat_ocr_dir = ""
    result = {}

    def __init__(self):
        if not self.common_paths or self.common_paths.strip() == "":
            raise ValueError("common_paths 不能为空字符串，请初始化该属性")
        if not self.ramdisk or self.ramdisk.strip() == "":
            raise ValueError("ramdisk 不能为空字符串，请初始化该属性")
        #查找路径
        self.wechat_dir = self.find_wechat_path()
        self.wechat_ocr_dir = self.find_wechatocr_exe()
        if not self.wechat_dir or self.wechat_dir.strip() == "":
            raise ValueError("wechat_dir 不能为空字符串，初始化wxOCR失败")
        if not self.wechat_ocr_dir or self.wechat_ocr_dir.strip() == "":
            raise ValueError("wechat_dir 不能为空字符串，初始化wxOCR失败")
        self.ocr_manager = OcrManager(self.wechat_dir)
        # 设置
        self.ocr_manager.SetExePath(self.wechat_ocr_dir)
        self.ocr_manager.SetUsrLibDir(self.wechat_dir)
        # 设置ocr识别结果的回调函数
        self.ocr_manager.SetOcrResultCallback(self.ocr_result_callback)
        # 启动ocr服务
        self.ocr_manager.StartWeChatOCR()

    # 开始识别图片
    def readtext(self,frame):
        # 清空之前的结果
        self.result = {}
        # 写入到临时文件
        image = Image.fromarray(frame)
        from datetime import datetime
        tmp_fname = self.ramdisk + str(datetime.now().timestamp()) +'.bmp'
        image.save(tmp_fname)    
        self.ocr_manager.DoOCRTask(tmp_fname)
        time.sleep(1)
        while self.ocr_manager.m_task_id.qsize() != OCR_MAX_TASK_ID:
            pass
        # 删除临时文件
        file_path = Path(tmp_fname)
        file_path.unlink(missing_ok=True)  # missing_ok=True 表示如果文件不存在也不会报错
        # 识别输出结果
        return self.result

    # 查找微信路径
    def find_wechat_path(self):
        # 定义匹配版本号文件夹的正则表达式
        version_pattern = re.compile(r'\[\d+\.\d+\.\d+\.\d+\]')
        path_temp = os.listdir(self.common_paths)
        for temp in path_temp:
            # 下载是正则匹配到[3.9.10.27]
            # 使用正则表达式匹配版本号文件夹
            if version_pattern.match(temp):
                wechat_path = os.path.join(self.common_paths, temp)
                if os.path.isdir(wechat_path):
                    return wechat_path
    
    # 查找微信OCR的路径
    def find_wechatocr_exe(self):
        # 获取APPDATA路径
        appdata_path = os.getenv("APPDATA")
        if not appdata_path:
            raise ValueError("APPDATA environment variable not found.")
    
        # 定义WeChatOCR的基本路径
        base_path = os.path.join(appdata_path, r"Tencent\\WeChat\\XPlugin\\Plugins\\WeChatOCR")
    
        # 定义匹配版本号文件夹的正则表达式
        version_pattern = re.compile(r'\d+')
    
        try:
            # 获取路径下的所有文件夹
            path_temp = os.listdir(base_path)
        except FileNotFoundError:
            print(f"The path {base_path} does not exist.")
            return None
    
        for temp in path_temp:
            # 使用正则表达式匹配版本号文件夹
            if version_pattern.match(temp):
                wechatocr_path = os.path.join(base_path, temp, 'extracted', 'WeChatOCR.exe')
                if os.path.isfile(wechatocr_path):
                    return wechatocr_path
    
        # 如果没有找到匹配的文件夹，返回 None
        return None
    # OCR 完成 执行的回调
    def ocr_result_callback(self,img_path:str, results:dict):
        print(f"识别成功")
        self.result = ''.join([item['text'].replace("\n", "").replace("\r", "") for item in results['ocrResult']])

    def __del__(self):
        self.ocr_manager.KillWeChatOCR()
