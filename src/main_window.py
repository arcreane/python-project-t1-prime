from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import QTimer
from src.widgets.radar_view import RadarView
from src.simulation.engine import SimulationEngine


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulation ATC")
        self.setGeometry(100, 100, 800, 600)
        self.engine = SimulationEngine()

        self.radar_view = RadarView(self.engine)

        control_widget = QWidget()
        control_layout = QVBoxLayout()
        self.start_button = QPushButton("Démarrer la simulation")
        self.start_button.clicked.connect(self.start_simulation)
        control_layout.addWidget(self.start_button)
        control_widget.setLayout(control_layout)

        self.setCentralWidget(self.radar_view)

        self.timer = QTimer(self)
        self.timer.setInterval(100)  # Met à jour toutes les 100 ms (10 FPS)
        self.timer.timeout.connect(self.update_simulation_step)

    def start_simulation(self):
        # Ajoutons un avion pour tester
        self.engine.add_test_aircraft()
        # Démarrer le "moteur"
        self.timer.start()
        self.start_button.setText("Simulation en cours...")
        self.start_button.setEnabled(False)

    def update_simulation_step(self):
        # 1. Faire avancer la simulation d'un "pas"
        self.engine.update()

        # 2. Demander au radar de se redessiner
        # (Qt le fait souvent seul si les données changent,
        # mais on force la mise à jour de la vue)
        self.radar_view.viewport().update()