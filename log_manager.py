import datetime

class LogManager:
    def __init__(self, canvas, width, height, max_lines=7, font=("Consolas", 10)):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.max_lines = max_lines
        self.font = font
        self.messages = []
        self.text_ids = []

        # Файл для логов
        self.logfile = open("log.txt", "a", encoding="utf-8")

    def log(self, message: str, timestamp=None):
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"

        # В лог-файл
        self.logfile.write(entry + "\n")
        self.logfile.flush()

        # В экранный лог
        self.messages.append(entry)
        if len(self.messages) > self.max_lines:
            self.messages = self.messages[-self.max_lines:]

    def draw(self):
        # Очистка предыдущих надписей
        for tid in self.text_ids:
            self.canvas.delete(tid)
        self.text_ids.clear()

        # Отрисовка последних сообщений
        padding = 10
        line_height = 16

        for i, msg in enumerate(reversed(self.messages)):
            y = self.height - padding - i * line_height
            tid = self.canvas.create_text(
                padding,
                y,
                anchor="sw",
                text=msg,
                fill="lightgray",
                font=self.font,
                tags="log_line"
            )
            self.text_ids.append(tid)

    def close(self):
        self.logfile.close()
