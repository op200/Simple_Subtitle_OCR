import sys

from ss_log import log

log.reset_cmd_color()


if len(sys.argv) <= 1:
    import ss_gui

    ss_gui.run_gui()


else:
    print("CLI 模式待做")
    # TODO: 命令行模式
