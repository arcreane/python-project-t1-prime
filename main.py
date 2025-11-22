import sys
import os

# Ajout du dossier src au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from PySide6.QtWidgets import QApplication
from src.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())