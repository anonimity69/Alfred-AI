import os
from datetime import datetime

class Logger:
    def __init__(self, log_dir="logs"):
        os.makedirs(log_dir, exist_ok=True)
        self.log_path = os.path.join(log_dir, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt")

    def log(self, text):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")
