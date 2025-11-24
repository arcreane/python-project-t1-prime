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
        self.holding = False  # Si True, l'avion part en circuit d'attente
        self.emergency_type = None
    def update_position(self, dt: float):
        """Met à jour la position (dt = delta time en secondes)."""
        if not self.active:
            return

        # 1. VITESSE : On réduit le coefficient (0.03 -> 0.015)
        # Les avions iront 2 fois moins vite.
        pixel_speed = self.speed * 0.015

        # Calcul trigonométrique
        rad = math.radians(self.heading - 90)
        self.x += math.cos(rad) * pixel_speed * dt
        self.y += math.sin(rad) * pixel_speed * dt

        # 2. CARBURANT : On réduit aussi la consommation (0.1 -> 0.05)
        # Sinon ils tomberont en panne car le vol est plus long !
        self.fuel -= 0.05 * dt

        if self.fuel <= 0:
            self.active = False
            print(f"CRASH: {self.callsign} panne d'essence !")