# 安装依赖
```
pip install opencv-python
pip install pillow
pip install easyocr
pip install numpy
```
如果需要GPU加速OCR，按[EasyOCR](https://github.com/JaidedAI/EasyOCR)中说明安装
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
判断前后帧的边缘差值，高于阈值的帧将被OCR`使用EazyOCR`
