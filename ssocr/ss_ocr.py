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
                from paddleocr import PaddleOCR

                return PaddleOCR
            except ModuleNotFoundError as e:
                log.error(f"存在未安装的库: {e}")

        case ocr_module.EasyOCR:
            try:
                import easyocr

                return easyocr
            except ModuleNotFoundError as e:
                log.error(f"存在未安装的库: {e}")
