import enum

import cv2

from ss_log import log
import ss_gui_var


class ocr_module(enum.Enum):
    PaddleOCR = "PaddleOCR"
    EasyOCR = "EasyOCR"
    WeChatOCR = "WeChatOCR"


class api:
    ocr_choice: ocr_module = ocr_module.PaddleOCR
    ocr_reader = None

    @staticmethod
    def switch_ocr_module(ocr_module: ocr_module):
        api.ocr_choice = ocr_module

        match ocr_module:
            case ocr_module.PaddleOCR:
                # 通过提前 import torch 防止 PaddleOCR 内部的 import 异常
                try:
                    import torch  # noqa: F401
                    from paddleocr import PaddleOCR

                    api.ocr_reader = PaddleOCR(
                        lang=ss_gui_var.set_language_Tkstr.get(),
                        use_gpu=ss_gui_var.open_gpu_Tkbool.get(),
                    )

                    return PaddleOCR

                except ModuleNotFoundError as e:
                    log.error(f"存在未安装的库: {e}")

            case ocr_module.EasyOCR:
                try:
                    import easyocr

                    api.ocr_reader = easyocr.Reader(
                        ss_gui_var.set_language_Tkstr.get().split(","),
                        gpu=ss_gui_var.open_gpu_Tkbool.get(),
                    )

                    return easyocr

                except ModuleNotFoundError as e:
                    log.error(f"存在未安装的库: {e}")

            case ocr_module.WeChatOCR:
                try:
                    from wx import WxOCR

                except ModuleNotFoundError as e:
                    log.error(f"存在未安装的库: {e}")

    @staticmethod
    def read(frame: cv2.typing.MatLike) -> str:
        match api.ocr_choice:
            case ocr_module.PaddleOCR:
                from paddleocr import PaddleOCR

                if not isinstance(api.ocr_reader, PaddleOCR):
                    raise Exception()

                text: str | None = api.ocr_reader.ocr(frame)[0]

                if text is None:
                    readed_text = [""]
                else:
                    readed_text = [line[1][0] for line in text]

            case ocr_module.EasyOCR:
                import easyocr

                if not isinstance(api.ocr_reader, easyocr.Reader):
                    raise Exception()

                readed_text = api.ocr_reader.readtext(frame, detail=0)

            case ocr_module.WeChatOCR:
                from wx import WxOCR

                if not isinstance(api.ocr_reader,WxOCR):
                    api.ocr_reader = WxOCR()

                readed_text = api.ocr_reader.readtext(frame)
                return readed_text

        return "\n".join(readed_text) + "\n"
