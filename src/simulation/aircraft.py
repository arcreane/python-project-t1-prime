import math


class Aircraft:
    def __init__(self, id, x, y, altitude, speed, heading):
        self.id = id
        self.x = x
        self.y = y
        self.altitude = altitude
        self.speed = speed  # Vitesse (en nœuds)
        self.heading = heading  # Cap (en degrés, 0=Nord, 90=Est)

    def move(self):
        """
        Met à jour la position de l'avion en fonction de sa vitesse et de son cap.
        C'est une simulation TRÈS simpliste !
        """
        # Convertir le cap en radians (math.sin/cos s'attendent à des radians)
        # Et ajuster pour le système de coordonnées (0° = Nord)
        rad_heading = math.radians(90 - self.heading)

        # Vitesse "par tick". On divise par 3600 (secondes/heure) et 10 (ticks/seconde)
        # C'est un exemple, la physique est à affiner !
        distance_per_tick = self.speed / 360

        self.x += distance_per_tick * math.cos(rad_heading)
        # Attention: en QGraphicsView, Y est inversé (vers le bas)
        self.y -= distance_per_tick * math.sin(rad_heading)

    def __repr__(self):
        return f"Aircraft(id={self.id}, pos=({self.x}, {self.y}))"