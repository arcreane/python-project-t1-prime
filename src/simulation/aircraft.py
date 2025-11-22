import math


class Aircraft:
    def __init__(self, callsign: str, x: float, y: float, heading: float, speed: float, altitude: int):
        self.callsign = callsign
        self.x = x
        self.y = y
        self.heading = heading  # En degrés (0-360)
        self.speed = speed  # En km/h (sera converti pour la simu)
        self.altitude = altitude
        self.fuel = 100.0  # Pourcentage
        self.landing_requested = False
        self.active = True  # Si False, l'avion a atterri ou crashé
        self.warning = False  # True si risque de collision
    def update_position(self, dt: float):
        """Met à jour la position (dt = delta time en secondes)."""
        if not self.active:
            return

        # MODIFICATION ICI : On passe de 0.1 à 0.03 pour ralentir le mouvement
        pixel_speed = self.speed * 0.03

        # Calcul trigonométrique pour le déplacement X/Y
        rad = math.radians(self.heading - 90)
        self.x += math.cos(rad) * pixel_speed * dt
        self.y += math.sin(rad) * pixel_speed * dt

        # Consommation carburant (ralentie aussi pour ne pas tomber en panne trop vite)
        self.fuel -= 0.1 * dt
        if self.fuel <= 0:
            self.active = False
            print(f"CRASH: {self.callsign} panne d'essence !")