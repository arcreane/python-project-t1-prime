from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QLabel, QPushButton, QListWidget, QGroupBox,
                               QListWidgetItem, QMessageBox) # <--- IMPORTANT : QListWidgetItem
from PySide6.QtGui import QColor                # <--- IMPORTANT : C'est celui qui te manque !
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

        # --- SCORE (Plus visible) ---
        self.score_label = QLabel("Score: 0")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom: 10px;")
        left_panel.addWidget(self.score_label)

        # --- TITRE LISTE ---
        lbl_titre = QLabel("RADAR TRAFFIC")
        lbl_titre.setStyleSheet("color: #888; font-weight: bold; margin-top: 10px;")
        left_panel.addWidget(lbl_titre)

        # --- LISTE DES AVIONS (Customisée pour le confort) ---
        self.plane_list = QListWidget()

        #
        self.plane_list.setStyleSheet("""
                    QListWidget {
                        background-color: #1e1e1e; /* Fond sombre */
                        border: 1px solid #444;
                        border-radius: 8px;
                        outline: none; /* Enlève le pointillé moche au focus */
                    }
                    QListWidget::item {
                        height: 50px;              /* GRANDE ZONE DE CLIC */
                        color: white;
                        font-size: 14px;
                        padding-left: 10px;
                        border-bottom: 1px solid #333; /* Ligne de séparation */
                    }
                    QListWidget::item:hover {
                        background-color: #333;    /* Gris au survol de la souris */
                    }
                    QListWidget::item:selected {
                        background-color: #0078d7; /* Bleu Windows quand sélectionné */
                        color: white;
                        font-weight: bold;
                        border-left: 5px solid white; /* Petite barre blanche décorative à gauche */
                    }
                """)

        # Connexion du clic
        self.plane_list.itemClicked.connect(self.on_list_clicked)

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

        # --- CIRCUIT D'ATTENTE (Nouveau) ---
        self.btn_hold = QPushButton("CIRCUIT D'ATTENTE")
        self.btn_hold.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
        self.btn_hold.clicked.connect(self.toggle_holding)
        ctrl_layout.addWidget(self.btn_hold)

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
        """Appelé régulièrement par le timer."""
        # 1. On vérifie si le jeu est fini
        if self.engine.game_over:
            self.timer.stop()

            # On récupère la raison précise stockée dans l'engine
            motif = self.engine.game_over_reason
            if not motif:
                motif = "Raison inconnue."

            # On affiche le message détaillé
            QMessageBox.critical(self, "GAME OVER",
                                 f"❌ MISSION ÉCHOUÉE ❌\n\n"
                                 f"Score final : {self.engine.score}\n"
                                 "-----------------------------\n"
                                 f"{motif}")
            self.close()
            return

        # 2. Mise à jour normale
        dt = 0.5
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
            for i, p in enumerate(self.engine.aircrafts):
                item = self.plane_list.item(i)

                # Texte de base
                display_text = f"{p.callsign} - Alt:{int(p.altitude)} - Fuel:{int(p.fuel)}%"

                # --- GESTION COULEURS & TEXTE URGENCE ---
                if p.emergency_type:
                    item.setForeground(QColor("red"))
                    # On change le texte pour afficher l'urgence !
                    item.setText(f"{p.callsign} - ⚠️ {p.emergency_type} ⚠️")

                elif p.landing_requested:
                    item.setForeground(QColor("#2ecc71"))
                    item.setText(display_text)
                elif p.holding:
                    item.setForeground(QColor("orange"))
                    item.setText(display_text)
                elif p.fuel < 20:
                    item.setForeground(QColor("#e74c3c"))
                    item.setText(display_text)
                else:
                    item.setForeground(QColor("white"))
                    item.setText(display_text)

    def on_list_clicked(self, item):
        """Action quand on clique sur la liste de gauche."""
        text = item.text()
        # Le texte est "AF123 - Alt:...", on récupère juste "AF123" (le premier mot)
        callsign = text.split(' ')[0]
        print(f"DEBUG: Clic liste sur {callsign}")
        self.on_plane_selected(callsign)

    def on_plane_selected(self, callsign):
        """Active les contrôles et met à jour la couleur du nom selon l'état."""
        print(f"DEBUG: Réception signal sélection pour {callsign}")

        found = False
        for p in self.engine.aircrafts:
            if p.callsign == callsign:
                self.selected_plane = p

                # Mise à jour du texte
                self.lbl_selected.setText(f"Avion: {callsign}")

                # --- GESTION DES COULEURS DU NOM ---
                if p.landing_requested:
                    # VERT = En cours d'atterrissage
                    self.lbl_selected.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 18px;")
                elif p.holding:
                    # ORANGE = En circuit d'attente
                    self.lbl_selected.setStyleSheet("color: orange; font-weight: bold; font-size: 18px;")
                else:
                    # BLANC = Vol normal
                    self.lbl_selected.setStyleSheet("color: white; font-weight: bold; font-size: 18px;")
                # -----------------------------------

                self.control_group.setEnabled(True)
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
            # Calcul de la nouvelle altitude théorique
            new_alt = self.selected_plane.altitude + delta

            # --- LOGIQUE DE SÉCURITÉ ---

            # CAS 1 : L'avion est en train d'atterrir
            if self.selected_plane.landing_requested:
                # On autorise la descente jusqu'à 0
                if new_alt < 0:
                    new_alt = 0

            # CAS 2 : L'avion est en vol normal
            else:
                # On INTERDIT de descendre en dessous de 500ft (Plancher de sécurité)
                if new_alt < 500:
                    new_alt = 500
                    print(
                        f"REFUSÉ : Altitude minimale de sécurité (500ft) atteinte pour {self.selected_plane.callsign}")

            # Application de l'altitude validée
            self.selected_plane.altitude = new_alt
            print(f"Nouvelle altitude : {self.selected_plane.altitude}")

    def request_landing(self):
        """Ordonne l'atterrissage et passe le nom en VERT."""
        if self.selected_plane:
            self.selected_plane.landing_requested = True

            # Si on atterrit, on arrête le circuit d'attente
            self.selected_plane.holding = False

            # On change la couleur immédiatement pour le feedback visuel
            self.lbl_selected.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 18px;")

            print(f"Atterrissage demandé pour {self.selected_plane.callsign}")

    def toggle_holding(self):
        """Active/Désactive l'attente et passe le nom en ORANGE."""
        if self.selected_plane:
            if self.selected_plane.fuel < 15:
                print(f"NÉGATIF : {self.selected_plane.callsign} Fuel Critique !")
                return

            self.selected_plane.holding = not self.selected_plane.holding

            if self.selected_plane.holding:
                # On annule l'atterrissage si on part en attente
                self.selected_plane.landing_requested = False
                # On met le texte en ORANGE
                self.lbl_selected.setStyleSheet("color: orange; font-weight: bold; font-size: 18px;")
                print(f"{self.selected_plane.callsign} rejoint le circuit d'attente.")
            else:
                # On repasse en BLANC (Vol normal)
                self.lbl_selected.setStyleSheet("color: white; font-weight: bold; font-size: 18px;")
                print(f"{self.selected_plane.callsign} reprend sa navigation.")