class Airport:
    def __init__(self, name: str, x: int, y: int, runway_angle: int):
        self.name = name
        self.x = x
        self.y = y
        self.runway_angle = runway_angle
        self.acceptance_radius = 50  # Distance en pixels pour valider l'atterrissage

    def can_land(self, aircraft) -> bool:
        """Vérifie si un avion est en condition d'atterrir."""
        dist = ((self.x - aircraft.x) ** 2 + (self.y - aircraft.y) ** 2) ** 0.5

        # Conditions : Proche, bonne altitude, vitesse réduite
        if dist < self.acceptance_radius and aircraft.altitude < 500 and aircraft.speed < 250:
            return True
        return False