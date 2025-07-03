import enum
import json

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
                try:
                    # 通过提前 import torch 防止 PaddleOCR 内部的 import 异常
                    # import torch  # noqa: F401
                    from paddleocr import PaddleOCR

                    if not hasattr(PaddleOCR, "predict"):
                        log.error("PaddleOCR 缺少 predict 方法, 可能是版本过低")

                    api.ocr_reader = PaddleOCR(
                        lang=ss_gui_var.set_language_Tkstr.get(),
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
        # cv2.imshow("Image", frame)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        match api.ocr_choice:
            case ocr_module.PaddleOCR:
                from paddleocr import PaddleOCR
                from paddlex.inference.pipelines.ocr.result import OCRResult

                if not isinstance(api.ocr_reader, PaddleOCR):
                    raise Exception()

                ocr_res: OCRResult = api.ocr_reader.predict(frame)[0]
                text: list[str] | None = ocr_res.get("rec_texts")

                if text is None:
                    readed_text = [""]
                else:
                    readed_text = text

            case ocr_module.EasyOCR:
                import easyocr

                if not isinstance(api.ocr_reader, easyocr.Reader):
                    raise Exception()

                readed_text = [str(t) for t in api.ocr_reader.readtext(frame, detail=0)]

        return "\n".join(readed_text) + "\n"

    @staticmethod
    def threshold_detection(img1: cv2.typing.MatLike, img2: cv2.typing.MatLike) -> int:
        score = cv2.quality.QualitySSIM.create(img1).compute(img2)

        # cv2.imshow("img1", img1)
        # cv2.imshow(f"img2 {1000 - score[0] * 1000}", img2)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return round(1000 - score[0] * 1000)
