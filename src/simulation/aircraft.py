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

    def update_position(self, dt: float):
        """Met à jour la position (dt = delta time en secondes)."""
        if not self.active:
            return

        # Conversion vitesse (km/h -> pixels/s arbitraire pour la simu)
        # On simplifie : 1 unite = 1 pixel
        pixel_speed = self.speed * 0.1

        # Calcul trigonométrique pour le déplacement X/Y
        rad = math.radians(self.heading - 90)  # -90 pour ajuster le 0° au Nord
        self.x += math.cos(rad) * pixel_speed * dt
        self.y += math.sin(rad) * pixel_speed * dt

        # Consommation carburant
        self.fuel -= 0.5 * dt
        if self.fuel <= 0:
            self.active = False
            print(f"CRASH: {self.callsign} panne d'essence !")