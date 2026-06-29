from gui.main_window import MainWindow
from core.logger import logger

logger.info("Aplicación iniciada.")

app = MainWindow()

app.mainloop()