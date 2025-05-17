# 安装依赖

推荐使用 Python 3.13

## 必要依赖库
```
pip install opencv-python
pip install pillow
pip install numpy
```


## 有两种OCR库可供选择

### 使用[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR/) (默认)
先安装[飞桨](https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/install/pip/windows-pip.html)  
再安装PaddleOCR
```
pip install paddleocr
```

### 使用[EasyOCR](https://github.com/JaidedAI/EasyOCR)
先安装[PyTorch](https://pytorch.org/)  
再安装EasyOCR
```
pip install easyocr
```

***

# 运行程序
```
python SS_OCR.py
```

***

# 使用说明
详见[Wiki](https://github.com/op200/Simple_Subtitle_OCR/wiki)

***

# 原理
判断前后帧的边缘差值，高于阈值的帧将被OCR
