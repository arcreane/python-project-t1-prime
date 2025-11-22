from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QFont
from PySide6.QtCore import Qt, Signal


class RadarView(QGraphicsView):
    # Signal émis quand on clique sur un avion (renvoie son callsign)
    aircraft_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(0, 0, 800, 600)
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))  # Fond radar sombre
        self.setRenderHint(QPainter.Antialiasing)

        # Stockage des items graphiques pour mise à jour optimisée
        self.aircraft_items = {}

    def draw_airport(self, airport):
        # Dessine la piste (statique)
        pen = QPen(Qt.white)
        pen.setWidth(3)
        self.scene.addLine(airport.x - 20, airport.y, airport.x + 20, airport.y, pen)

        # Cercle vert pour mieux voir l'aéroport
        self.scene.addEllipse(airport.x - 5, airport.y - 5, 10, 10, QPen(Qt.green), QBrush(Qt.green))

        text = self.scene.addText(airport.name)
        text.setDefaultTextColor(Qt.white)
        text.setPos(airport.x - 20, airport.y + 10)

    def update_radar(self, aircrafts):
        """Met à jour l'affichage des avions."""
        active_callsigns = set()

        for plane in aircrafts:
            if not plane.active:
                continue

            active_callsigns.add(plane.callsign)

            # Gestion des couleurs
            color = Qt.yellow
            if plane.landing_requested: color = Qt.green

            if plane.fuel < 20: color = Qt.red  # [cite: 71]

            # --- MISE À JOUR OU CRÉATION ---
            if plane.callsign in self.aircraft_items:
                # Mise à jour existante
                items = self.aircraft_items[plane.callsign]
                items['ellipse'].setRect(plane.x - 5, plane.y - 5, 10, 10)
                items['ellipse'].setPen(QPen(color))
                items['ellipse'].setBrush(QBrush(color))

                items['text'].setPos(plane.x + 10, plane.y)
                items['text'].setPlainText(f"{plane.callsign}\n{plane.altitude}ft")
                items['text'].setDefaultTextColor(color)
            else:
                # Création nouvelle
                # 1. Le point (Avion)
                ellipse = self.scene.addEllipse(plane.x - 5, plane.y - 5, 10, 10, QPen(color), QBrush(color))
                ellipse.setZValue(10)  # S'assure que le point est au-dessus
                ellipse.setData(0, plane.callsign)  # IMPORTANT: Stocke l'ID pour le clic

                # 2. Le texte (Info)
                text = self.scene.addText(f"{plane.callsign}\n{plane.altitude}ft")
                text.setDefaultTextColor(color)
                text.setPos(plane.x + 10, plane.y)
                text.setData(0, plane.callsign)  # IMPORTANT: Le texte devient aussi cliquable !

                self.aircraft_items[plane.callsign] = {'ellipse': ellipse, 'text': text}

        # Nettoyage des avions disparus
        known_callsigns = list(self.aircraft_items.keys())
        for callsign in known_callsigns:
            if callsign not in active_callsigns:
                self.scene.removeItem(self.aircraft_items[callsign]['ellipse'])
                self.scene.removeItem(self.aircraft_items[callsign]['text'])
                del self.aircraft_items[callsign]

    def mousePressEvent(self, event):
        """Gestion du clic robuste."""
        # On récupère l'item sous la souris
        item = self.itemAt(event.pos())

        if item:
            # On récupère la donnée "0" stockée (le callsign)
            callsign = item.data(0)
            if callsign:
                print(f"Clic détecté sur : {callsign}")  # Debug console
                self.aircraft_selected.emit(callsign)
            else:
                print("Item cliqué mais pas d'avion associé")

        super().mousePressEvent(event)