# 安装依赖

项目使用 Python 3.13 开发和测试，不保证其他版本兼容，且 <3.11 的版本一定不兼容

## 必要依赖库
在安装 OCR 库之后安装，防止 OCR 库依赖的版本覆盖新版，若已被覆盖，可先卸载 `pip uninstall opencv-contrib-python` 再安装
```
pip install -U opencv-contrib-python
pip install -U pillow
pip install -U numpy
```


## 选择你想用的 OCR 库

### 使用 [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR/) (默认)

> [!CAUTION]
> SSOCR v0.10.0 开始不再支持 PaddleOCR v2 API  
> PaddleOCR 版本必须 >= 3.1.0

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

***

# 运行程序

* 旧版
  ```
  python SS_OCR.py
  ```

* 新版  
  双击运行 `ssocr.pyz` 文件  
  或在其他窗口调用 `python ssocr.pyz`

***

# 使用说明
详见 [Wiki](https://github.com/op200/Simple_Subtitle_OCR/wiki)

***

# 原理
判断前后帧的差值，高于阈值的帧将被OCR，可以将阈值设为 `-2` 以跳过阈值检测直接 OCR
