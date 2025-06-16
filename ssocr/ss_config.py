import os
import configparser
import platform

from ss_log import log
import ss_ocr
import ss_info
import ss_gui_var

# 判断系统对应路径
os_type = platform.system()
if os_type == "Windows":
    config_dir = os.path.join(os.getenv("APPDATA") or "", "SS_OCR")
elif os_type == "Linux" or os_type == "Darwin":
    config_dir = os.path.join(os.path.expanduser("~"), ".config", "SS_OCR")
else:
    config_dir = ""
    log.warning("无法确认系统")

os.makedirs(config_dir, exist_ok=True)

ocr_choice: ss_ocr.ocr_module = ss_ocr.ocr_module.PaddleOCR

# 不存在配置则写入默认配置
config = configparser.ConfigParser()
config_file_pathname = os.path.join(config_dir, "config.ini")
if (
    not os.path.exists(config_file_pathname)
    or config.read(config_file_pathname)
    and config.get("DEFAULT", "version") != ss_info.PROJECT_VERSION
):
    config["DEFAULT"] = {
        k: str(v)
        for k, v in {
            "version": ss_info.PROJECT_VERSION,
            "ocr": ss_ocr.ocr_module.PaddleOCR.value,
            "language": "ch",
            "srt_path": r".\output.srt",
            "srt_overwrite": 0,
            "use_gpu": 0,
            "set_filter": 0,
            "retain_color_tolerance": 10,
            "retain_color1": "#ffffff",
            "retain_color2": "#000000",
        }.items()
    }
    with open(config_file_pathname, "w") as configfile:
        config.write(configfile)


def save_config():
    config["DEFAULT"]["language"] = ss_gui_var.set_language_Tkstr.get()
    config["DEFAULT"]["srt_path"] = ss_gui_var.set_srtPath_Tkstr.get()
    config["DEFAULT"]["srt_overwrite"] = (
        "1" if ss_gui_var.srt_overwrite_Tkbool.get() else "0"
    )
    config["DEFAULT"]["use_gpu"] = "1" if ss_gui_var.open_gpu_Tkbool.get() else "0"
    config["DEFAULT"]["set_filter"] = "1" if ss_gui_var.set_filter_Tkbool.get() else "0"
    config["DEFAULT"]["retain_color_tolerance"] = str(
        ss_gui_var.retain_color_tolerance_Tkint.get()
    )
    config["DEFAULT"]["retain_color1"] = ss_gui_var.retain_color1_Tkstr.get()
    config["DEFAULT"]["retain_color2"] = ss_gui_var.retain_color2_Tkstr.get()

    try:
        with open(config_file_pathname, "w") as configfile:
            config.write(configfile)
    except FileNotFoundError:
        pass


ss_gui_var.open_gpu_Tkbool.set(bool(int(config.get("DEFAULT", "use_gpu"))))
ss_gui_var.srt_overwrite_Tkbool.set(bool(int(config.get("DEFAULT", "srt_overwrite"))))
ss_gui_var.set_filter_Tkbool.set(bool(int(config.get("DEFAULT", "set_filter"))))
ss_gui_var.retain_color_tolerance_Tkint.set(
    int(config.get("DEFAULT", "retain_color_tolerance"))
)
ss_gui_var.retain_color1_Tkstr.set(config.get("DEFAULT", "retain_color1"))
ss_gui_var.retain_color2_Tkstr.set(config.get("DEFAULT", "retain_color2"))
