import random
from simulation.aircraft import Aircraft
from simulation.airport import Airport
import math


class SimulationEngine:
    def __init__(self):
        self.aircrafts = []
        self.airport = Airport("IPSA-Tower", 400, 300, 270)
        self.score = 0
        self.time_elapsed = 0
        self.game_over = False  # Le jeu est en cours
        self.game_over_reason = ""  # Pour stocker le motif précis

        # --- CONFIGURATION DIFFICULTÉ ---
        self.max_aircraft_limit = 10  # MODIFIÉ : Plafond fixé à 10 avions maximum
        self.spawn_interval = 12  # Un nouvel avion autorisé toutes les 12s

        # On commence avec 4 avions
        for _ in range(4):
            self.spawn_aircraft()

    def spawn_aircraft(self):
        """Génère un avion avec compagnie, altitude et CARBURANT réalistes."""

        # 1. CHOIX DE LA COMPAGNIE (Liste étendue)
        airlines = [
            "AF", "BA", "LH", "DL", "UA", "AA", "KLM", "EZY", "RYR", "UAE",
            "QTR", "JAL", "ANA", "SIA", "CPA", "IB", "LX", "AZ", "AC", "QFA", "TAP", "SAS"
        ]
        company = random.choice(airlines)
        number = random.randint(10, 9999)
        callsign = f"{company}{number}"

        # 2. POSITION & CAP
        side = random.randint(0, 3)
        if side == 0:  # Gauche
            x, y, heading = 0, random.randint(50, 550), random.randint(45, 135)
        elif side == 1:  # Droite
            x, y, heading = 800, random.randint(50, 550), random.randint(225, 315)
        elif side == 2:  # Haut
            x, y, heading = random.randint(50, 750), 0, random.randint(135, 225)
        else:  # Bas
            x, y, heading = random.randint(50, 750), 600, random.randint(315, 405)

        # 3. ALTITUDE ALÉATOIRE (3000ft - 8000ft)
        random_alt = random.randint(6, 16) * 500

        # 4. CRÉATION DE L'AVION
        new_plane = Aircraft(callsign, x, y, heading, speed=280, altitude=random_alt)

        # --- AJOUT RÉALISME CARBURANT ---
        # En approche, le réservoir n'est jamais plein.
        # On génère une valeur entre 15% (Critique) et 40% (Confortable)
        new_plane.fuel = random.randint(25, 40)
        # --------------------------------

        self.aircrafts.append(new_plane)
        print(f"SPAWN: {callsign} à {random_alt}ft avec {new_plane.fuel}% Fuel")

    def update(self, dt: float):
        """Boucle principale de simulation"""
        self.time_elapsed += dt

        # --- 1. GESTION DU SPAWN (Difficulté croissante) ---
        # Formule : 4 avions de base + 1 avion toutes les 12 secondes
        allowed_planes = 4 + int(self.time_elapsed / self.spawn_interval)
        # On vérifie chaque frame. 0.2% de chance par frame qu'un incident arrive.
        # Cela fait environ un incident toutes les 30 à 60 secondes.
        if random.random() < 0.002:
            # On choisit un avion au hasard qui n'a PAS encore de problème et qui n'atterrit pas
            candidates = [p for p in self.aircrafts if p.emergency_type is None and not p.landing_requested]

            if candidates:
                victim = random.choice(candidates)

                # Choix du type de problème
                incident = random.choice(["PANNE MOTEUR", "MALAISE", "DÉPRESSURISATION"])
                victim.emergency_type = incident

                # Conséquence immédiate (Gameplay)
                if incident == "PANNE MOTEUR":
                    victim.speed = 150  # L'avion ralentit brutalement
                elif incident == "DÉPRESSURISATION":
                    # Il doit descendre d'urgence ! (On ne le force pas, c'est au joueur de le faire)
                    pass

                print(f"URGENCE DÉCLENCHÉE : {victim.callsign} - {incident}")

        # On bloque au plafond défini (ex: 10 ou 15 avions)
        if allowed_planes > self.max_aircraft_limit:
            allowed_planes = self.max_aircraft_limit

        # Si il y a de la place, on a une chance de faire apparaître un avion
        if len(self.aircrafts) < allowed_planes:
            # 5% de chance par frame (Rythme fluide)
            if random.random() < 0.05:
                self.spawn_aircraft()

        # --- 2. MISE À JOUR DE CHAQUE AVION ---
        # On itère sur une copie [:] pour pouvoir supprimer des éléments sans bug
        for plane in self.aircrafts[:]:

            # A. MODE ATTERRISSAGE (Prioritaire)
            if plane.landing_requested:
                # Vitesse d'approche réduite
                plane.speed = 200

                # Calculs de distance
                dist_to_airport = ((self.airport.x - plane.x) ** 2 + (self.airport.y - plane.y) ** 2) ** 0.5
                diff_y = self.airport.y - plane.y
                diff_x = self.airport.x - plane.x

                # Alignement Y (Phase 1)
                if abs(diff_y) > 5:
                    plane.heading = 180 if diff_y > 0 else 360
                # Alignement X + Descente (Phase 2)
                else:
                    plane.heading = 90 if diff_x > 0 else 270

                    # Pente de descente (Glide Slope)
                    target_altitude = dist_to_airport * 6.0
                    plane.altitude = min(plane.altitude, target_altitude)

                    # Force 0 si très proche
                    if dist_to_airport < 10:
                        plane.altitude = 0.0

            # B. MODE CIRCUIT D'ATTENTE (Holding Pattern)
            elif plane.holding:
                import math

                # Point pivot (150, 150)
                hold_x, hold_y = 150, 150

                # MODIFICATION ICI : On réduit le rayon de 60 à 25 pixels
                orbit_radius = 25

                # Calculs
                dx = plane.x - hold_x
                dy = plane.y - hold_y
                dist_hold = (dx ** 2 + dy ** 2) ** 0.5
                angle_to_center = math.atan2(dy, dx)

                # LOGIQUE D'ORBITE
                if dist_hold > orbit_radius + 20:  # On augmente la marge d'approche
                    # On vise le centre pour entrer
                    target_angle = angle_to_center + math.pi
                    plane.heading = math.degrees(target_angle)

                else:
                    # On tourne autour (Tangente)
                    # Le facteur de correction maintient l'avion sur le rail de 25px
                    correction = 0
                    if dist_hold > orbit_radius: correction = 0.5  # Correction plus forte
                    if dist_hold < orbit_radius: correction = -0.5

                    tangent_angle = angle_to_center + (math.pi / 2) + correction
                    plane.heading = math.degrees(tangent_angle)

            # C. VOL NORMAL (Manuel)
            # L'avion suit juste son cap actuel (géré par update_position)

            # --- 3. APPLICATION DU MOUVEMENT ---
            plane.update_position(dt)

            # GESTION PANNE SÈCHE -> GAME OVER PRÉCIS
            plane.fuel -= 0.05 * dt
            if plane.fuel <= 0:
                self.game_over = True
                self.game_over_reason = f"PANNE SÈCHE :\nLe vol {plane.callsign} s'est écrasé faute de carburant !"
                return

            # --- 4. VÉRIFICATIONS D'ÉTAT ---

            # Distance finale pour valider l'atterrissage
            dist_final = ((self.airport.x - plane.x) ** 2 + (self.airport.y - plane.y) ** 2) ** 0.5

            # SUCCÈS : Atterrissage réussi
            if plane.landing_requested and plane.altitude == 0 and dist_final < 5:
                plane.active = False
                self.score += 100
                self.aircrafts.remove(plane)
                print(f"{plane.callsign} ATTERRI ! Score: {self.score}")

            # NETTOYAGE : Avion sorti de la zone radar (Marge de 100px)
            elif plane.x < -100 or plane.x > 900 or plane.y < -100 or plane.y > 700:
                plane.active = False
                self.aircrafts.remove(plane)
                print(f"SORTIE RADAR : {plane.callsign}")

            # CRASH / PANNE : Avion inactif
            elif not plane.active:
                self.aircrafts.remove(plane)

        # --- 5. VÉRIFICATION COLLISIONS ---
        self.check_collisions()

    def check_collisions(self):
        """Si deux avions se touchent -> GAME OVER avec noms."""
        for p in self.aircrafts:
            p.warning = False

        for i, p1 in enumerate(self.aircrafts):
            for p2 in self.aircrafts[i + 1:]:
                dist = ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5
                alt_diff = abs(p1.altitude - p2.altitude)

                # ALERTE (Orange/Rouge)
                if dist < 80 and alt_diff < 400:
                    p1.warning = True
                    p2.warning = True

                    # CRASH RÉEL (< 20px) -> GAME OVER
                    if dist < 20:
                        self.game_over = True
                        # ON ENREGISTRE LES NOMS DES COUPABLES
                        self.game_over_reason = (f"COLLISION AÉRIENNE :\n"
                                                 f"Le vol {p1.callsign} a percuté le vol {p2.callsign}\n"
                                                 f"à une altitude de {int(p1.altitude)}ft.")
                        print(f"GAME OVER : {self.game_over_reason}")
                        return