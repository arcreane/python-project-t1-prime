from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QFont
from PySide6.QtCore import Qt, Signal


class RadarView(QGraphicsView):
    aircraft_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(0, 0, 800, 600)
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setRenderHint(QPainter.Antialiasing)

        self.aircraft_items = {}

        # --- NOUVEAU : DESSINER LE POINT D'ATTENTE ---
        # Coordonnées du point (150, 150)
        self.scene.addEllipse(145, 145, 10, 10, QPen(Qt.cyan), QBrush(Qt.cyan))
        text_hold = self.scene.addText("HOLD")
        text_hold.setDefaultTextColor(Qt.cyan)
        text_hold.setPos(135, 160)
        # ---------------------------------------------

    # ... (Le reste des méthodes draw_airport, update_radar, mousePressEvent reste identique)
    # Si tu as besoin je peux te remettre tout le fichier, mais c'est juste l'init qui change ici.

    def draw_airport(self, airport):
        # ... (Garde ton code existant) ...
        pen = QPen(Qt.white)
        pen.setWidth(3)
        self.scene.addLine(airport.x - 20, airport.y, airport.x + 20, airport.y, pen)
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

            # --- GESTION DES COULEURS (ORDRE DE PRIORITÉ) ---
            color = Qt.yellow  # 1. Couleur par défaut (Vol normal)

            if plane.landing_requested:
                color = Qt.green  # 2. Atterrissage
            elif plane.holding:
                color = QColor("orange")  # 3. Attente
            elif plane.fuel < 20:
                color = QColor("orange")  # 4. Fuel bas

            # 5. Pannes / Urgences (Important)
            if plane.emergency_type is not None:
                color = Qt.red

            # 6. RISQUE COLLISION (PRIORITÉ ABSOLUE)
            # C'est ce bloc qui manquait ou était mal placé !
            if plane.warning:
                color = Qt.red
            # ------------------------------------------------

            # Préparation du texte
            label_text = f"{plane.callsign}\n{int(plane.altitude)}ft"
            if plane.emergency_type:
                label_text += f"\n⚠️ {plane.emergency_type}"
            if plane.warning:  # On ajoute aussi un petit texte visuel
                label_text += "\n⚠️ COLLISION ?"

            # --- DESSIN ---
            if plane.callsign in self.aircraft_items:
                items = self.aircraft_items[plane.callsign]
                items['ellipse'].setRect(plane.x - 5, plane.y - 5, 10, 10)
                items['ellipse'].setPen(QPen(color))
                items['ellipse'].setBrush(QBrush(color))

                items['text'].setPos(plane.x + 10, plane.y)
                items['text'].setPlainText(label_text)
                items['text'].setDefaultTextColor(color)
            else:
                ellipse = self.scene.addEllipse(plane.x - 5, plane.y - 5, 10, 10, QPen(color), QBrush(color))
                ellipse.setZValue(10)
                ellipse.setData(0, plane.callsign)

                text = self.scene.addText(label_text)
                text.setDefaultTextColor(color)
                text.setPos(plane.x + 10, plane.y)
                text.setData(0, plane.callsign)

                self.aircraft_items[plane.callsign] = {'ellipse': ellipse, 'text': text}

        # Nettoyage
        known_callsigns = list(self.aircraft_items.keys())
        for callsign in known_callsigns:
            if callsign not in active_callsigns:
                self.scene.removeItem(self.aircraft_items[callsign]['ellipse'])
                self.scene.removeItem(self.aircraft_items[callsign]['text'])
                del self.aircraft_items[callsign]

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            callsign = item.data(0)
            if callsign:
                self.aircraft_selected.emit(callsign)
        super().mousePressEvent(event)