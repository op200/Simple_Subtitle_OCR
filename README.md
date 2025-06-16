# 安装依赖

项目使用 Python 3.13 开发和测试，不保证其他版本兼容，且 <3.11 的版本一定不兼容

## 必要依赖库
```
pip install -U opencv-python
pip install -U pillow
pip install -U numpy
```


## 选择你想用的 OCR 库

### 使用 [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR/) (默认)

> [!CAUTION]
> PaddleOCR 的新版本 (v3.0.1) 不兼容 Python 3.13 等环境  
> 若需要使用新版，可以用其他 Python 版本  
> 若仅需要使用旧版，指定旧版本以安装 `pip install paddleocr==2.10.0`

先安装 [飞桨](https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/install/pip/windows-pip.html)  
再安装 PaddleOCR

```
pip install paddleocr
```

### 使用 [EasyOCR](https://github.com/JaidedAI/EasyOCR)

先安装 [PyTorch](https://pytorch.org/)  
再安装 EasyOCR

```
pip install easyocr
```

### 使用 [WeChatOCR](https://github.com/kanadeblisst00/wechat_ocr)（本分支添加的功能）

仅支持windows系统，测试 微信windows客户端 3.9.12.51 版本可用，先安装 [微信](https://pc.weixin.qq.com)  
再打开 ssocr/wx.py 修改配置
```
common_paths = "" # 这个是微信的安装路径 例如下面这个
#common_paths = r"C:\\Program Files (x86)\\Tencent\WeChat"
ramdisk = "" # 这里是一个内存盘的盘符，因为微信ocr不支持从内存直接读取数据，只能先写入文件 所以需要利用 ramdisk 创建一个路径，tool文件夹下带了一个魔方内存盘 我在测试的时候创建了一个L盘 配置方法例如下面这句
#ramdisk = "L:/"
```
```
# 安装依赖
pip install wechat_ocr
```
打开 tool 下的 ramdisk.exe 创建一个内存盘，并且分配上面配置的对应盘符


***

# 运行程序

* 旧版
  ```
  python SS_OCR.py
  ```

* 新版  
  双击运行 `ssocr.pyz` 文件  
  或在其他窗口调用 `python ssocr.pyz`

* 新版（本分支）
  ```
  python __main__.py
  ```
***

# 使用说明
详见 [Wiki](https://github.com/op200/Simple_Subtitle_OCR/wiki)

***

# 原理
判断前后帧的差值，高于阈值的帧将被OCR，可以将阈值设为 `-2` 以跳过阈值检测直接 OCR
