import sys

from ss_log import log

# os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

log.reset_cmd_color()


if len(sys.argv) <= 1:
    import ss_gui

    ss_gui.run_gui()


else:
    print("CLI 模式待做")
    # TODO: 命令行模式
