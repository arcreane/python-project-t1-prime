from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtCore import Qt


class RadarView(QGraphicsView):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine  # Garde une référence vers le moteur de simulation
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.init_scene()

    def init_scene(self):
        # Définir la taille de la scène (par exemple, 2000x2000 pixels)
        self.scene.setSceneRect(-1000, -1000, 2000, 2000)
        self.setBackgroundBrush(QBrush(QColor(0, 30, 0)))  # Fond vert foncé

        # Dessiner des cercles radar
        pen = QPen(QColor(0, 100, 0))  # Vert radar
        self.scene.addEllipse(-250, -250, 500, 500, pen)
        self.scene.addEllipse(-500, -500, 1000, 1000, pen)
        self.scene.addEllipse(-750, -750, 1500, 1500, pen)

        self.setRenderHint(QPainter.Antialiasing)  # Pour des cercles lisses

    def paintEvent(self, event):
        # D'abord, laisser QGraphicsView dessiner la scène (le fond, les cercles)
        super().paintEvent(event)

        # Ensuite, on va dessiner les avions PAR-DESSUS.
        # C'est une astuce. On pourrait aussi les ajouter comme objets QGraphicsItem
        # dans la scène, ce qui est plus propre mais plus complexe à gérer.

        # Pour ce projet, le plus simple est de mettre à jour les "QGraphicsItem"
        # On va le faire dans une méthode séparée
        self.update_aircraft_on_scene()

    def update_aircraft_on_scene(self):
        # 1. Effacer tous les anciens avions de la scène
        # (C'est basique, on peut optimiser plus tard)
        for item in self.scene.items():
            if item.data(0) == "aircraft":  # On "tag" nos avions
                self.scene.removeItem(item)
                del item

        # 2. Redessiner tous les avions depuis le moteur
        pen = QPen(Qt.yellow)
        brush = QBrush(Qt.yellow)

        for aircraft in self.engine.aircrafts:
            # Dessiner l'avion (un simple point)
            dot = self.scene.addEllipse(aircraft.x, aircraft.y, 10, 10, pen, brush)
            dot.setData(0, "aircraft")  # "Tag" l'item comme un avion

            # Dessiner son identifiant
            text = self.scene.addText(f"{aircraft.id}\n{int(aircraft.altitude)}ft")
            text.setDefaultTextColor(Qt.yellow)
            text.setPos(aircraft.x + 10, aircraft.y)
            text.setData(0, "aircraft")  # "Tag" aussi le texte