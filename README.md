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
