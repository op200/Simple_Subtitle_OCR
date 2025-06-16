import tkinter as tk


class log:
    log_Text: tk.Text

    @staticmethod
    def output(info: str):
        try:
            log.log_Text.insert(tk.END, info + "\n")
            log.log_Text.see(tk.END)
        except NameError:
            pass
        print(info)

    @staticmethod
    def error(info: str):
        log.output(f"[ERROR] {info}")

    @staticmethod
    def warning(info: str):
        log.output(f"[WARNING] {info}")

    @staticmethod
    def info(info: str):
        log.output(f"[INFO] {info}")
