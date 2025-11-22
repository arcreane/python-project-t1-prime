from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QLabel, QPushButton, QListWidget, QGroupBox)
from PySide6.QtCore import QTimer, Qt
from .simulation.engine import SimulationEngine
from .widgets.radar_view import RadarView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATC Simulator - IPSA 2025")
        self.resize(1200, 700)

        # --- Initialisation Simulation ---
        self.engine = SimulationEngine()
        self.selected_plane = None

        # --- Interface ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # 1. Panel Gauche : Liste des avions & Stats [cite: 69]
        left_panel = QVBoxLayout()
        self.score_label = QLabel("Score: 0")
        self.plane_list = QListWidget()
        left_panel.addWidget(self.score_label)
        left_panel.addWidget(QLabel("Avions détectés:"))
        left_panel.addWidget(self.plane_list)
        layout.addLayout(left_panel, 1)

        # 2. Zone Centrale : Radar [cite: 69]
        self.radar = RadarView()
        self.radar.aircraft_selected.connect(self.on_plane_selected)
        layout.addWidget(self.radar, 3)

        # 3. Panel Droit : Contrôles [cite: 70]
        right_panel = QVBoxLayout()

        self.control_group = QGroupBox("Ordres de Vol")
        self.control_group.setEnabled(False)  # Désactivé si pas de sélection
        ctrl_layout = QVBoxLayout()

        self.lbl_selected = QLabel("Aucune sélection")
        ctrl_layout.addWidget(self.lbl_selected)

        btn_left = QPushButton("Cap -10°")
        btn_left.clicked.connect(lambda: self.change_heading(-10))

        btn_right = QPushButton("Cap +10°")
        btn_right.clicked.connect(lambda: self.change_heading(10))

        btn_land = QPushButton("AUTORISER ATTERRISSAGE")  # [cite: 65]
        btn_land.setStyleSheet("background-color: green; color: white;")
        btn_land.clicked.connect(self.request_landing)

        ctrl_layout.addWidget(btn_left)
        ctrl_layout.addWidget(btn_right)
        ctrl_layout.addWidget(btn_land)

        self.control_group.setLayout(ctrl_layout)
        right_panel.addWidget(self.control_group)
        right_panel.addStretch()
        layout.addLayout(right_panel, 1)

        # --- Timer de Simulation ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(100)  # 10 fps pour commencer

    def game_loop(self):
        """Appelé 10 fois par seconde."""
        dt = 0.5  # Temps simulé par frame
        self.engine.update(dt)

        # Mise à jour visuelle
        self.radar.update_radar(self.engine.aircrafts)
        self.update_ui_stats()

    def update_ui_stats(self):
        self.score_label.setText(f"Score: {self.engine.score}")
        # Mise à jour liste (simplifiée)
        self.plane_list.clear()
        for p in self.engine.aircrafts:
            self.plane_list.addItem(f"{p.callsign} - Alt:{p.altitude} - Fuel:{int(p.fuel)}%")

    def on_plane_selected(self, callsign):
        # Trouve l'avion correspondant
        for p in self.engine.aircrafts:
            if p.callsign == callsign:
                self.selected_plane = p
                self.lbl_selected.setText(f"Avion: {callsign}")
                self.control_group.setEnabled(True)
                break

    def change_heading(self, delta):
        if self.selected_plane:
            self.selected_plane.heading = (self.selected_plane.heading + delta) % 360

    def request_landing(self):
        if self.selected_plane:
            self.selected_plane.landing_requested = True
            self.selected_plane.altitude = 0  # Simplification pour l'exemple