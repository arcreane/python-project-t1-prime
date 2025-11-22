from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QLabel, QPushButton, QListWidget, QGroupBox)
from PySide6.QtCore import QTimer, Qt
from simulation.engine import SimulationEngine
from widgets.radar_view import RadarView


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

        # 1. Panel Gauche : Liste des avions & Stats
        left_panel = QVBoxLayout()
        self.score_label = QLabel("Score: 0")

        self.plane_list = QListWidget()
        # NOUVEAU : On connecte le clic sur la liste à une fonction
        self.plane_list.itemClicked.connect(self.on_list_clicked)

        left_panel.addWidget(self.score_label)
        left_panel.addWidget(QLabel("Avions détectés:"))
        left_panel.addWidget(self.plane_list)
        layout.addLayout(left_panel, 1)

        # 2. Zone Centrale : Radar
        self.radar = RadarView()
        self.radar.aircraft_selected.connect(self.on_plane_selected)
        # On dessine l'aéroport au démarrage
        self.radar.draw_airport(self.engine.airport)
        layout.addWidget(self.radar, 3)

        # 3. Panel Droit : Contrôles
        right_panel = QVBoxLayout()

        self.control_group = QGroupBox("Ordres de Vol")
        self.control_group.setEnabled(False)  # Désactivé par défaut

        ctrl_layout = QVBoxLayout()

        # Label de sélection
        self.lbl_selected = QLabel("Aucune sélection")
        self.lbl_selected.setAlignment(Qt.AlignCenter)
        ctrl_layout.addWidget(self.lbl_selected)

        # Gestion du CAP (Horizontal)
        h_layout_cap = QHBoxLayout()
        btn_left = QPushButton("↺ -10°")
        btn_left.clicked.connect(lambda: self.change_heading(-10))
        btn_right = QPushButton("+10° ↻")
        btn_right.clicked.connect(lambda: self.change_heading(10))
        h_layout_cap.addWidget(btn_left)
        h_layout_cap.addWidget(btn_right)
        ctrl_layout.addLayout(h_layout_cap)

        # Gestion de l'ALTITUDE (Horizontal)
        h_layout_alt = QHBoxLayout()
        btn_descend = QPushButton("Descendre")
        btn_descend.clicked.connect(lambda: self.change_altitude(-500))
        btn_climb = QPushButton("Monter")
        btn_climb.clicked.connect(lambda: self.change_altitude(500))
        h_layout_alt.addWidget(btn_descend)
        h_layout_alt.addWidget(btn_climb)
        ctrl_layout.addLayout(h_layout_alt)

        # ATTERRISSAGE
        btn_land = QPushButton("AUTORISER ATTERRISSAGE")
        btn_land.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        btn_land.clicked.connect(self.request_landing)
        ctrl_layout.addWidget(btn_land)

        self.control_group.setLayout(ctrl_layout)
        right_panel.addWidget(self.control_group)
        right_panel.addStretch()
        layout.addLayout(right_panel, 1)

        # --- Timer de Simulation ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(100)  # 10 fps

    def game_loop(self):
        """Appelé 10 fois par seconde."""
        dt = 0.5  # Temps simulé par frame
        self.engine.update(dt)

        # Mise à jour visuelle
        self.radar.update_radar(self.engine.aircrafts)
        self.update_ui_stats()

    def update_ui_stats(self):
        self.score_label.setText(f"Score: {self.engine.score}")

        # Astuce : On ne vide pas la liste tout le temps pour éviter de perdre la sélection
        # On met à jour seulement le texte si le nombre d'items correspond, sinon on refait.
        if self.plane_list.count() != len(self.engine.aircrafts):
            self.plane_list.clear()
            for p in self.engine.aircrafts:
                self.plane_list.addItem(f"{p.callsign} - Alt:{int(p.altitude)} - Fuel:{int(p.fuel)}%")
        else:
            # Mise à jour du texte des items existants sans détruire la sélection
            for i, p in enumerate(self.engine.aircrafts):
                item = self.plane_list.item(i)
                item.setText(f"{p.callsign} - Alt:{int(p.altitude)} - Fuel:{int(p.fuel)}%")

    def on_list_clicked(self, item):
        """Action quand on clique sur la liste de gauche."""
        text = item.text()
        # Le texte est "AF123 - Alt:...", on récupère juste "AF123" (le premier mot)
        callsign = text.split(' ')[0]
        print(f"DEBUG: Clic liste sur {callsign}")
        self.on_plane_selected(callsign)

    def on_plane_selected(self, callsign):
        """Active les contrôles pour l'avion donné."""
        print(f"DEBUG: Réception signal sélection pour {callsign}")

        found = False
        for p in self.engine.aircrafts:
            if p.callsign == callsign:
                self.selected_plane = p
                self.lbl_selected.setText(f"Avion: {callsign}")
                self.control_group.setEnabled(True)  # Active les boutons
                found = True
                break

        if not found:
            print(f"Erreur: Avion {callsign} non trouvé dans l'engine")

    def change_heading(self, delta):
        if self.selected_plane:
            self.selected_plane.heading = (self.selected_plane.heading + delta) % 360
            print(f"Nouveau cap : {self.selected_plane.heading}")

    def change_altitude(self, delta):
        if self.selected_plane:
            new_alt = self.selected_plane.altitude + delta
            if new_alt < 0: new_alt = 0
            self.selected_plane.altitude = new_alt
            print(f"Nouvelle altitude : {self.selected_plane.altitude}")

    def request_landing(self):
        if self.selected_plane:
            self.selected_plane.landing_requested = True
            print(f"Atterrissage demandé pour {self.selected_plane.callsign}")