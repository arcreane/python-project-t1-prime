from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem
from PySide6.QtGui import QPen, QBrush, QColor, QPainter
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

        self.plane_items = {}  # Dictionnaire pour garder trace des objets graphiques

    def draw_airport(self, airport):
        # Dessine la piste
        pen = QPen(Qt.white)
        pen.setWidth(3)
        self.scene.addLine(airport.x - 20, airport.y, airport.x + 20, airport.y, pen)
        text = self.scene.addText(airport.name)
        text.setDefaultTextColor(Qt.white)
        text.setPos(airport.x - 20, airport.y + 10)

    def update_radar(self, aircrafts):
        """Met à jour l'affichage des avions."""
        # Nettoyage simple (pourrait être optimisé)
        self.scene.clear()

        # Redessine l'aéroport (devrait être stocké, mais simplifié ici)
        # Note: Dans une version avancée, l'aéroport est un item permanent.
        center_x, center_y = 400, 300
        self.scene.addEllipse(center_x - 5, center_y - 5, 10, 10, QPen(Qt.green), QBrush(Qt.green))

        for plane in aircrafts:
            if not plane.active:
                continue

            # Dessin de l'avion (Cercle + Ligne de direction)
            color = Qt.yellow if not plane.landing_requested else Qt.green
            if plane.fuel < 20: color = Qt.red  # Alerte carbu [cite: 71]

            # Point représentant l'avion
            ellipse = self.scene.addEllipse(plane.x - 5, plane.y - 5, 10, 10, QPen(color), QBrush(color))
            ellipse.setData(0, plane.callsign)  # Stocke l'ID pour le clic

            # Étiquette texte
            text = self.scene.addText(f"{plane.callsign}\n{plane.altitude}ft")
            text.setDefaultTextColor(color)
            text.setPos(plane.x + 10, plane.y)

    def mousePressEvent(self, event):
        """Gestion du clic pour sélectionner un avion."""
        item = self.itemAt(event.pos())
        if item and isinstance(item, QGraphicsEllipseItem):
            callsign = item.data(0)
            if callsign:
                self.aircraft_selected.emit(callsign)
        super().mousePressEvent(event)