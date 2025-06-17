import enum

import cv2

from ss_log import log
import ss_gui_var


if not hasattr(cv2, "quality"):
    log.error("OpenCV 版本不匹配, 将无法使用阈值检测")


class ocr_module(enum.Enum):
    PaddleOCR = "PaddleOCR"
    EasyOCR = "EasyOCR"


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
                    log.error(f"导入 PaddleOCR 时存在未安装的库: {e}")

            case ocr_module.EasyOCR:
                try:
                    import easyocr

                    api.ocr_reader = easyocr.Reader(
                        ss_gui_var.set_language_Tkstr.get().split(","),
                        gpu=ss_gui_var.open_gpu_Tkbool.get(),
                    )

                    return easyocr

                except ModuleNotFoundError as e:
                    log.error(f"导入 EasyOCR 时存在未安装的库: {e}")

    @staticmethod
    def ocr(frame: cv2.typing.MatLike) -> str:
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

        return "\n".join(readed_text) + "\n"

    @staticmethod
    def threshold_detection(img1: cv2.typing.MatLike, img2: cv2.typing.MatLike) -> int:
        ssim = cv2.quality.QualitySSIM.create(img1)
        score = ssim.compute(img2)

        return round(1000 - score[0] * 1000)
