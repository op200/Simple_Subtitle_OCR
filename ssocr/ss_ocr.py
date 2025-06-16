import enum

from ss_log import log


class ocr_module(enum.Enum):
    PaddleOCR = enum.auto()
    EasyOCR = enum.auto()


def switch_ocr_module(ocr_module: ocr_module):
    match ocr_module:
        case ocr_module.PaddleOCR:
            # 通过提前 import torch 防止 PaddleOCR 内部的 import 异常
            try:
                import torch  # noqa: F401
            except ModuleNotFoundError:
                pass
            try:
                from paddleocr import PaddleOCR  # noqa: F401
            except ModuleNotFoundError:
                log.error("未安装库: paddleocr")

        case ocr_module.EasyOCR:
            try:
                import easyocr  # noqa: F401
            except ModuleNotFoundError:
                log.error("未安装库: easyocr")
